import { execSync } from "node:child_process";

// 1. 读取输入
const input = JSON.parse(process.env.SKILL_INPUT ?? "{}");
const prompt: string = input.prompt;
const duration: number = input.duration ?? 5;

// 2. 调用视频生成 API（以 Replicate 为例）
const response = await fetch("https://api.replicate.com/v1/predictions", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.REPLICATE_API_TOKEN}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    version: "your-model-version-id",
    input: { prompt, num_frames: duration * 8 },
  }),
});

const prediction = await response.json();
let result = prediction;

// 3. 轮询等待完成
while (result.status !== "succeeded" && result.status !== "failed") {
  await new Promise((resolve) => setTimeout(resolve, 5000));
  const pollResponse = await fetch(
    `https://api.replicate.com/v1/predictions/${result.id}`,
    {
      headers: {
        Authorization: `Bearer ${process.env.REPLICATE_API_TOKEN}`,
      },
    },
  );
  result = await pollResponse.json();
}

if (result.status === "failed") {
  console.error("Video generation failed:", result.error);
  process.exit(1);
}

// 4. 下载视频
const videoUrl = result.output;
const videoResponse = await fetch(videoUrl);
const videoBuffer = Buffer.from(await videoResponse.arrayBuffer());

const outputPath = "/tmp/output.mp4";
const fs = await import("node:fs");
fs.writeFileSync(outputPath, videoBuffer);

// 5. 上传结果
execSync(
  `bash "${process.env.GITHUB_WORKSPACE}/lib/common/upload-result.sh" "${outputPath}"`,
  { stdio: "inherit" },
);

console.log("Video generated and uploaded");

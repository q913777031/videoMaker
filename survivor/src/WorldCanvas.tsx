import React, { useLayoutEffect, useRef } from "react";
import { Cam, H, W, drawWorld } from "./world";

/** 世界层：每帧按时间 t 与相机重新绘制全部 1024 人（纯函数，同帧重复渲染结果一致） */
export const WorldCanvas: React.FC<{ t: number; cam: Cam; style?: React.CSSProperties }> = ({ t, cam, style }) => {
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => {
    const ctx = ref.current?.getContext("2d");
    if (ctx) drawWorld(ctx, t, cam);
  }, [t, cam]);
  return <canvas ref={ref} width={W} height={H} style={{ position: "absolute", left: 0, top: 0, ...style }} />;
};

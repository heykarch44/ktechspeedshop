export function formatDate(date: Date) {
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function statusLabel(status: string) {
  return status.replace("-", " ");
}

export type VideoEmbed = {
  type: "youtube" | "vimeo" | "file";
  src: string;
};

export function parseVideo(url?: string): VideoEmbed | undefined {
  if (!url) return;
  const trimmed = url.trim();
  const yt = trimmed.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/
  );
  if (yt) {
    return {
      type: "youtube",
      src: `https://www.youtube-nocookie.com/embed/${yt[1]}`,
    };
  }
  const vimeo = trimmed.match(/vimeo\.com\/(?:video\/)?(\d+)/);
  if (vimeo) {
    return {
      type: "vimeo",
      src: `https://player.vimeo.com/video/${vimeo[1]}`,
    };
  }
  return { type: "file", src: trimmed };
}

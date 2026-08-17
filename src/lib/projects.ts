import { getCollection, type CollectionEntry } from "astro:content";

export type Project = CollectionEntry<"projects">;
export type Update = CollectionEntry<"updates">;

export async function getProjects() {
  const projects = await getCollection("projects");
  return projects.sort((a, b) => b.data.year - a.data.year);
}

export async function getProject(slug: string) {
  const projects = await getCollection("projects");
  return projects.find((project) => project.id === slug);
}

export async function getUpdates(projectSlug?: string) {
  const updates = await getCollection("updates");
  const filtered = projectSlug
    ? updates.filter((update) => update.data.project === projectSlug)
    : updates;
  return filtered.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );
}

export function coverFor(update: Update) {
  return update.data.images[0];
}

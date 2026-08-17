import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const journal = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/journal" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    image: z.string(),
    tags: z.array(z.string()).default([]),
  }),
});

const projects = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/projects" }),
  schema: z.object({
    title: z.string(),
    year: z.number(),
    model: z.string(),
    nickname: z.string().optional(),
    status: z.enum([
      "planning",
      "in-build",
      "paint",
      "assembly",
      "complete",
      "for-sale",
    ]),
    cover: z.string(),
    summary: z.string(),
    specs: z.array(z.string()).default([]),
    featured: z.boolean().default(true),
  }),
});

const updates = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/updates" }),
  schema: z.object({
    project: z.string(),
    title: z.string(),
    pubDate: z.coerce.date(),
    summary: z.string().optional(),
    images: z.array(z.string()).default([]),
    video: z.string().optional(),
  }),
});

export const collections = { journal, projects, updates };

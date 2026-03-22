import type { Project } from "../context/AppContext";

export const INITIAL_PROJECTS: Project[] = [
  {
    id: "p1",
    name: "Job Search",
    emoji: "💼",
    color: "#6366F1",
    tasks: [
      {
        id: "t1", title: "Build a Resume", done: false, urgent: true, timeEstimate: "45 min",
        subtasks: [
          { id: "s1", title: "Pick a clean template from Canva", done: true, tinyStart: true },
          { id: "s2", title: "Write 3 bullet points for last role", done: false, tinyStart: true },
          { id: "s3", title: "Add education & skills section", done: false },
          { id: "s4", title: "Export as PDF and save to Drive", done: false },
        ],
      },
      {
        id: "t2", title: "Apply to 5 companies", done: false, urgent: false, timeEstimate: "1.5 hrs",
        subtasks: [
          { id: "s5", title: "Make a list of 5 target companies", done: false, tinyStart: true },
          { id: "s6", title: "Customize cover letter intro for each", done: false },
          { id: "s7", title: "Submit applications on their sites", done: false },
        ],
      },
      {
        id: "t3", title: "Prep for interviews", done: false, urgent: false, timeEstimate: "2 hrs",
        subtasks: [
          { id: "s8", title: "Write your '30-second story'", done: false, tinyStart: true },
          { id: "s9", title: "Practice STAR answers for 3 questions", done: false },
          { id: "s10", title: "Research the company's recent news", done: false },
        ],
      },
    ],
  },
  {
    id: "p2",
    name: "Apartment Move",
    emoji: "🏠",
    color: "#F59E0B",
    tasks: [
      {
        id: "t4", title: "Find a new apartment", done: false, urgent: true, timeEstimate: "30 min",
        subtasks: [
          { id: "s11", title: "Set budget & neighborhood preferences", done: true, tinyStart: true },
          { id: "s12", title: "Browse 10 listings on Zillow", done: false, tinyStart: true },
          { id: "s13", title: "Schedule 3 viewings this week", done: false },
        ],
      },
      {
        id: "t5", title: "Pack belongings", done: false, urgent: false, timeEstimate: "3 hrs",
        subtasks: [
          { id: "s14", title: "Get boxes from the grocery store", done: false, tinyStart: true },
          { id: "s15", title: "Pack books & non-essentials first", done: false },
          { id: "s16", title: "Label each box by room", done: false },
        ],
      },
    ],
  },
  {
    id: "p3",
    name: "Side Project",
    emoji: "🚀",
    color: "#10B981",
    tasks: [
      {
        id: "t6", title: "Design the landing page", done: false, urgent: false, timeEstimate: "1 hr",
        subtasks: [
          { id: "s17", title: "Sketch a wireframe on paper (2 min)", done: false, tinyStart: true },
          { id: "s18", title: "Pick a color palette", done: false },
          { id: "s19", title: "Build the hero section in code", done: false },
        ],
      },
    ],
  },
];

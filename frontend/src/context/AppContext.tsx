import { createContext, useContext } from "react";

export interface Subtask {
  id: string;
  title: string;
  done: boolean;
  tinyStart?: boolean;
}

export interface Task {
  id: string;
  title: string;
  done: boolean;
  urgent: boolean;
  timeEstimate: string;
  subtasks: Subtask[];
  _projectColor?: string;
}

export interface Project {
  id: string;
  name: string;
  emoji: string;
  color: string;
  tasks: Task[];
}

export interface AppContextType {
  projects: Project[];
  activeProject: string | null;
  setActiveProject: (id: string | null) => void;
  activeFilter: string | null;
  setActiveFilter: (filter: string | null) => void;
  toggleSubtask: (taskId: string, subtaskId: string) => void;
}

export const AppContext = createContext<AppContextType | null>(null);

export function useAppContext(): AppContextType {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppContext.Provider");
  return ctx;
}

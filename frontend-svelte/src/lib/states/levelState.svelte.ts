import type { Level } from "../../types";
import { fetchLevels } from "../../api/level";

interface LevelState {
  levels: Level[];
  isLoading: boolean;
  error: string | null;
}

export const levelState = $state<LevelState>({
  levels: [],
  isLoading: false,
  error: null
});

/**
 * Fetches all levels and updates the state
 */
export async function refreshLevels(): Promise<void> {
  levelState.isLoading = true;
  levelState.error = null;
  
  try {
    levelState.levels = await fetchLevels();
  } catch (err) {
    levelState.error = err instanceof Error ? err.message : 'Failed to fetch levels';
    console.error('Error fetching levels:', err);
  } finally {
    levelState.isLoading = false;
  }
}

/**
 * Gets a level by ID from the current state
 * @param id - The level ID to find
 * @returns The level object or undefined if not found
 */
export function getLevelById(id: number): Level | undefined {
  return levelState.levels.find(level => level.id === id);
}

/**
 * Gets a level name by ID from the current state
 * @param id - The level ID to find
 * @returns The level name or undefined if not found
 */
export function getLevelNameById(id: number): string | undefined {
  return getLevelById(id)?.name;
}

/**
 * Gets levels by curriculum ID from the current state
 * @param curriculumId - The curriculum ID to filter by
 * @returns An array of levels for the specified curriculum
 */
export function getLevelsByCurriculumId(curriculumId: number): Level[] {
  return levelState.levels.filter(level => level.curriculum_id === curriculumId);
}

/**
 * Gets a formatted level display string (curriculum name + level name)
 * @param id - The level ID to find
 * @returns Formatted string like "Math: Level 1" or undefined if not found
 */
export function getLevelDisplayById(id: number): string | undefined {
  const level = getLevelById(id);
  if (!level?.curriculum) return undefined;
  
  return `${level.curriculum.name}: ${level.name}`;
}
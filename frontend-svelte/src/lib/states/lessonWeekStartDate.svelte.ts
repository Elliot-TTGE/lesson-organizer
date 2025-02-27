import { getStartOfWeekInUTC } from "$lib/utils/dateUtils";

export const lessonWeekStartDate = $state({current: getStartOfWeekInUTC(new Date())});
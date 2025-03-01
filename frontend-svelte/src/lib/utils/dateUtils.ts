export function getStartOfWeekInUTC(date: Date): Date {
    const day = date.getUTCDay();
    const diff = date.getUTCDate() - day;
    const sunday = new Date(date.setDate(diff));

    // Set time to midnight local time
    sunday.setHours(0, 0, 0, 0);
    
    // Convert to UTC
    return sunday;
}

export function isWithinOneWeek(date1: Date, date2: Date): boolean {
    const startOfWeek1 = getStartOfWeekInUTC(date1);
    const startOfWeek2 = getStartOfWeekInUTC(date2);
    
    const diffInDays = Math.abs((startOfWeek2.getTime() - startOfWeek1.getTime()) / (1000 * 60 * 60 * 24));
    return diffInDays < 7;
}
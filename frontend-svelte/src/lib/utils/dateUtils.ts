export function getStartOfWeekInUTC(date: Date): Date {
    const day = date.getUTCDay();
    const diff = date.getUTCDate() - day;
    const sunday = new Date(date.setDate(diff));
    
    // Set time to midnight local time
    sunday.setHours(0, 0, 0, 0);
    
    // Convert to UTC
    const utcSunday = new Date(Date.UTC(sunday.getFullYear(), sunday.getMonth(), sunday.getDate(), 0, 0, 0));
    
    return utcSunday;
}
export function getStartOfWeekInUTC(date: Date): Date {
    const day = date.getDay();
    const newDate = date.getDate() - day;
    const sunday = new Date(date.setDate(newDate));

    // Set time to midnight local time
    sunday.setHours(0, 0, 0, 0);

    return sunday;
}

export function isWithinOneWeek(startOfWeek: Date, dateToCompare: Date): boolean {
    const dateToCompareStartOfWeek = getStartOfWeekInUTC(dateToCompare);

    return startOfWeek.toUTCString() === dateToCompareStartOfWeek.toUTCString();
}
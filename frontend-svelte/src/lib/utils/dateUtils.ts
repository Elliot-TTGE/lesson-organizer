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

export function initializeDateTimeInput(datetime: string = new Date().toISOString()) {
    const localDate = new Date(datetime);
    const offset = localDate.getTimezoneOffset() * 60000; // offset in milliseconds
    const localISOTime = new Date(localDate.getTime() - offset).toISOString().slice(0, 16);
    return {
      date: localISOTime.split('T')[0],
      time: localISOTime.split('T')[1],
    };
  }
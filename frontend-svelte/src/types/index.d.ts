export interface Student {
  id: number;
  first_name: string;
  last_name: string;
  created_date: string;
  status: 'active' | 'inactive' | 'hold' | 'trial';
  levels: Level[];
}

export interface Lesson {
  id: number;
  datetime: string;
  plan: string;
  concepts: string;
  notes: string;
  students: Student[];
  created_date: string;
}

export interface Quiz {
  id: number;
  name: string;
  datetime: string;
  score: number;
  notes: string;
  lesson_id: number;
  student_id: number;
}

export interface Level {
  id: number;
  student_id: number;
  start_date: string;
  level_category: string;
}

export interface User {
  id: number;
  first_name: string;
  last_name: string;
  created_date: string;
  last_login?: string;
  password: string;
  role: string;
}

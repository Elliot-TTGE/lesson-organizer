// Students
export interface Student {
  id: number;
  created_date: string;
  updated_date: string;
  first_name: string;
  last_name?: string;
  date_started?: string;
  classes_per_week?: number;
  notes_general?: string;
  notes_strengths?: string;
  notes_weaknesses?: string;
  notes_future?: string;
  lessons: Lesson[];
  status_history: StudentStatusHistory[];
  level_history: StudentLevelHistory[];
  quizzes: StudentLessonQuiz[];
}

export interface StudentStatus {
  id: number;
  name: string;
}

export interface StudentStatusHistory {
  id: number;
  created_date: string;
  updated_date: string;
  student_id: number;
  status_id: number;
  changed_at: string;
}

export interface StudentLevelHistory {
  id: number
  created_date: string;
  updated_date: string;
  student_id: number;
  level_id: number;
  start_date: string;
}

// Lessons
export interface Lesson {
  id: number;
  created_date: string;
  updated_date: string;
  datetime: string;
  plan?: string;
  concepts?: string;
  notes?: string;
  students: Student[];
}

export interface LessonStudent {
  id: number;
  created_date: string;
  updated_date: string;
  lesson_id: number;
  student_id: number;
}

// Quizzes
export interface Quiz {
  id: number;
  created_date: string;
  updated_date: string;
  name: string;
  max_points: number;
  unit_id?: number;
  unit: Unit;
}

export interface StudentLessonQuiz {
  id: number;
  created_date: string;
  updated_date: string;
  student_id: number;
  lesson_id: number;
  quiz_id: number;
  points: number;
  notes: string;
}

// Curriculum
export interface Curriculum {
  id: number;
  created_date: string;
  updated_date: string;
  name: string;
  levels: Level[];
}

export interface Level {
  id: number;
  created_date: string;
  updated_date: string;
  name: string;
  curriculum_id: number;
  curriculum: Curriculum;
  student_level_history: StudentLevelHistory[];
  units: Unit[];
}
export interface Unit {
  id: number;
  created_date: string;
  updated_date: string;
  name: string;
  level_id: number;
  level: Level;
  quizzes: Quiz[];
}

// User
export interface User {
  id: number;
  created_date: string;
  updated_date: string;
  first_name: string;
  last_name: string;
  last_login?: string;
  email: string;
  password: string;
  role: string;
}

export interface Pagination {
  page: number;
  per_page: number;
  pages: number;
  total: number;
}
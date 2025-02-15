import type { Student, Lesson, Quiz, Level, User } from './types/index.d.ts';

const BASE_URL = 'http://192.168.68.51:4000';

interface RequestOptions {
    method: string;
    headers: { [key: string]: string };
    body?: string;
}

interface QueryParams {
    [key: string]: string | number | boolean;
}

interface JSendResponse<T> {
    status: 'success' | 'fail' | 'error';
    data?: T;
    message?: string;
}

function buildQueryString(params: QueryParams): string {
    return Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
}

async function apiRequest<T>(endpoint: string, method: string = 'GET', body: any = null, headers: { [key: string]: string } = {}, params: QueryParams = {}): Promise<T> {
    let url = `${BASE_URL}/api${endpoint}`;
    if (Object.keys(params).length > 0) {
        const queryString = buildQueryString(params);
        url += `?${queryString}`;
    }
    
    const options: RequestOptions = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...headers
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const jsonResponse: JSendResponse<T> = await response.json();

    if (jsonResponse.status === 'success') {
        return jsonResponse.data as T;
    } else if (jsonResponse.status === 'fail' || jsonResponse.status === 'error') {
        throw new Error(jsonResponse.message || 'An error occured while reading errored json response.');
    }

    throw new Error('Unexpected response format');
}

// Student

export async function fetchStudents(params: QueryParams = {}): Promise<Student[]> {
    return await apiRequest<Student[]>('/students', 'GET', null, {}, params);
}

export async function createStudent(student: Student): Promise<Student> {
    return await apiRequest<Student>('/students', 'POST', student);
}

// Lesson

export async function fetchLessons(params: QueryParams = {}): Promise<Lesson[]> {
    return await apiRequest<Lesson[]>('/lessons', 'GET', null, {}, params);
}

export async function createLesson(lesson: Partial<Lesson>): Promise<Lesson> {
    return await apiRequest<Lesson>('/lessons', 'POST', lesson);
}

// Quiz

export async function fetchQuizzes(params: QueryParams = {}): Promise<Quiz[]> {
    return await apiRequest<Quiz[]>('/quizzes', 'GET', null, {}, params);
}

export async function createQuiz(quiz: Quiz): Promise<Quiz> {
    return await apiRequest<Quiz>('/quizzes', 'POST', quiz);
}

// Level

export async function fetchLevels(params: QueryParams = {}): Promise<Level[]> {
    return await apiRequest<Level[]>('/levels', 'GET', null, {}, params);
}

export async function createLevel(level: Level): Promise<Level> {
    return await apiRequest<Level>('/levels', 'POST', level);
}

// User

export async function fetchUsers(params: QueryParams = {}): Promise<User[]> {
    return await apiRequest<User[]>('/students', 'GET', null, {}, params);
}

export async function createUser(user: User): Promise<User> {
    return await apiRequest<User>('/users', 'POST', user);
}
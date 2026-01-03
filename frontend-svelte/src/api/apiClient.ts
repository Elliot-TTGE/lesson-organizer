// Determine API URL with fallback logic
const getApiBaseUrl = (): string => {
    // Priority 1: Build-time environment variable
    if (import.meta.env.VITE_API_BASE_URL) {
        return import.meta.env.VITE_API_BASE_URL;
    }
    
    // Priority 2: Auto-detection based on access method
    if (typeof window !== 'undefined' && import.meta.env.MODE === 'production') {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        const port = window.location.port;
        
        // If accessed with explicit port (like :3000), assume direct access - use :4000
        // If no port or standard ports (80/443), assume reverse proxy - use /api path
        if (port && port !== '80' && port !== '443') {
            return `${protocol}//${hostname}:4000`;
        } else {
            return `${protocol}//${hostname}/api`;
        }
    }
    
    // Priority 3: Development default
    return 'http://localhost:4000';
};

const BASE_URL: string = getApiBaseUrl();

export interface QueryParams {
    [key: string]: string | number | boolean;
}

interface JSendResponse<T> {
    status: 'success' | 'fail' | 'error';
    data?: T;
    message?: string;
}

interface RequestOptions {
    method: string;
    headers: { [key: string]: string };
    body?: string;
    credentials?: RequestCredentials
}

function buildQueryString(params: QueryParams): string {
    return Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
}

function getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
    return null;
}

export async function apiRequest<T>(endpoint: string, method: string = 'GET', body: any = null, headers: { [key: string]: string } = {}, params: QueryParams = {}): Promise<T> {
    let url = `${BASE_URL}/api${endpoint}`;
    if (Object.keys(params).length > 0) {
        const queryString = buildQueryString(params);
        url += `?${queryString}`;
    }
    
    const csrfToken = getCookie('csrf_access_token');
    const options: RequestOptions = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...headers,
            ...(csrfToken ? { 'X-CSRF-TOKEN': csrfToken } : {})
        },
        credentials: "include"
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    if (!response.ok) {
        throw response;
    }

    if (response.status === 204) {
        return {} as T;
    }
    
    const jsonResponse: JSendResponse<T> = await response.json();

    if (jsonResponse.status === 'success') {
        return jsonResponse.data as T;
    } else if (jsonResponse.status === 'fail' || jsonResponse.status === 'error') {
        throw new Error(jsonResponse.message || 'An error occurred while reading errored json response.');
    }

    throw new Error('Unexpected response format');
}

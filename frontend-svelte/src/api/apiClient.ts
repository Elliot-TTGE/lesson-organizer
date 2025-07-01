const BASE_URL: string = import.meta.env.VITE_API_BASE_URL;

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
    
    //const token = getCookie('token');
    const csrfToken = getCookie('csrf_access_token');
    const options: RequestOptions = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...headers,
            //...(token ? { 'Authorization': `Bearer ${token}` } : {}),
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

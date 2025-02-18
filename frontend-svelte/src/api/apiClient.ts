const BASE_URL = import.meta.env.VITE_API_BASE_URL;

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
}

function buildQueryString(params: QueryParams): string {
    return Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
}

export async function apiRequest<T>(endpoint: string, method: string = 'GET', body: any = null, headers: { [key: string]: string } = {}, params: QueryParams = {}): Promise<T> {
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

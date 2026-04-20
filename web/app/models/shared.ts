import { Observable } from "rxjs";

export interface APIOperations<T, ID> {
    get(pagination?: PageMeta): Observable<Page>;
    getById(id: ID): Observable<T>;
    getByName(name: string, pagination?: PageMeta): Observable<Page>;
    removeById(id: ID): Observable<T>;
    save(data: Partial<T>): Observable<T>;
    update(id: ID, data: T): Observable<T>;
}
export interface APIErrorResponse {
    code: number;
    details: string;
    message: string;
    method: string;
    url: string;
}

export interface Language {
    id: string;
    name: string;
}

export interface PageMeta {
    total_elements: number;
    total_pages: number;
    per_page: number;
    page: number;
}

export interface Page {
    data: [],
    metadata: PageMeta,
}

export class DefaultPageMeta implements PageMeta {
    page: number = 1;
    per_page: number = 10;
    total_elements: number = 0;
    total_pages: number = 1;
}
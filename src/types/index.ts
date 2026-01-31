export interface Question {
    id: any;
    text: string;
    image: string;
    image_path?: string;
    page: number;
    subject?: string;
    image_base64?: string;
    created_at?: string;
    difficulty?: number;
    topic?: string;
}

export interface Template {
    id: number;
    name: string;
    path: string;
    preview_image: string;
    margins_json: string;
}

export interface Margins {
    top: number;
    bottom: number;
    left: number;
    right: number;
}

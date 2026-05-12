import { User } from "./user";

export interface OIDCToken {
    id_token: string;
    profile:User;
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
    status: boolean;
    provider: string;
    created_on: string;
}
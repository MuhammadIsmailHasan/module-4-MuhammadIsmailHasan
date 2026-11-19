/** Typed client used by Client Components. Components never call fetch directly. */
import { ApiError, request, type RequestOptions } from "./http";
import { clearSession, getToken } from "./session";
import type {
  ActivityEntry,
  Analytics,
  AuthResult,
  Attachment,
  Board,
  Card,
  Category,
  Column,
  Comment,
  Inbox,
  Notification,
  Priority,
  Subtask,
  User,
} from "./types";

async function call<T>(method: string, path: string, opts: RequestOptions = {}): Promise<T> {
  try {
    return await request<T>(method, path, { token: getToken(), ...opts });
  } catch (err) {
    if (err instanceof ApiError && err.httpStatus === 401 && typeof window !== "undefined" && getToken()) {
      // an expired or invalid Token: drop it and go to login (never loop on the login call itself)
      clearSession();
      window.location.assign("/login");
    }
    throw err;
  }
}

const get = <T>(path: string, query?: RequestOptions["query"]) => call<T>("GET", path, { query });
const pageQuery = (p: PageQuery) => ({ limit: p.limit === undefined ? undefined : String(p.limit), before: p.before });
const post = <T>(path: string, body?: unknown) => call<T>("POST", path, { body });
const patch = <T>(path: string, body?: unknown) => call<T>("PATCH", path, { body });
const del = <T>(path: string) => call<T>("DELETE", path);

export interface CardInput {
  title?: string;
  description?: string | null;
  priority?: Priority;
  start_date?: string | null;
  end_date?: string | null;
  category_id?: string | null;
  assignee_id?: string | null;
}

/** Paging for the Inbox and the activity lists (Decision J). */
export interface PageQuery {
  limit?: number;
  before?: string;
}

export interface Candidate {
  id: string;
  full_name: string;
}

export interface CardFilters {
  search?: string;
  priority?: string;
  assignee?: string;
  category?: string;
}

export const api = {
  auth: {
    register: (body: { full_name: string; login_identifier: string; password: string }) =>
      request<AuthResult>("POST", "/auth/register", { body }),
    login: (body: { login_identifier: string; password: string }) =>
      request<AuthResult>("POST", "/auth/login", { body }),
    logout: () => post<null>("/auth/logout"),
  },
  boards: {
    list: () => get<Board[]>("/boards"),
    get: (id: string) => get<Board>(`/boards/${id}`),
    create: (body: { name: string; visibility?: "public" | "private"; description?: string }) => post<Board>("/boards", body),
    update: (id: string, body: { name?: string; visibility?: string; owner_id?: string | null }) =>
      patch<Board>(`/boards/${id}`, body),
    members: (id: string) => get<User[]>(`/boards/${id}/members`),
    addMember: (id: string, userId: string) => post<User>(`/boards/${id}/members`, { user_id: userId }),
    removeMember: (id: string, userId: string) => del<null>(`/boards/${id}/members/${userId}`),
    activity: (id: string, page: PageQuery = {}) => get<ActivityEntry[]>(`/boards/${id}/activity`, pageQuery(page)),
    candidates: (id: string, search: string) => get<Candidate[]>(`/boards/${id}/candidates`, { search: search || undefined }),
    addColumn: (id: string, name: string) => post<Column>(`/boards/${id}/columns`, { name }),
  },
  cards: {
    listForBoard: (boardId: string, f: CardFilters = {}) =>
      get<Card[]>(`/boards/${boardId}/cards`, {
        search: f.search,
        "filter[priority]": f.priority,
        "filter[assignee]": f.assignee,
        "filter[category]": f.category,
      }),
    get: (id: string) => get<Card>(`/cards/${id}`),
    activity: (id: string, page: PageQuery = {}) => get<ActivityEntry[]>(`/cards/${id}/activity`, pageQuery(page)),
    create: (columnId: string, body: CardInput & { title: string }) => post<Card>(`/columns/${columnId}/cards`, body),
    update: (id: string, body: CardInput) => patch<Card>(`/cards/${id}`, body),
    move: (id: string, body: { column_id: string; prev?: string | null; next?: string | null }) =>
      patch<Card>(`/cards/${id}/move`, body),
    archive: (id: string) => post<Card>(`/cards/${id}/archive`),
    remove: (id: string) => del<null>(`/cards/${id}`),
  },
  subtasks: {
    create: (cardId: string, title: string) => post<Subtask>(`/cards/${cardId}/subtasks`, { title }),
    update: (id: string, body: { title?: string; is_done?: boolean; prev?: string | null; next?: string | null }) =>
      patch<Subtask>(`/subtasks/${id}`, body),
    remove: (id: string) => del<null>(`/subtasks/${id}`),
  },
  attachments: {
    addLink: (cardId: string, body: { url: string; name?: string }) =>
      post<Attachment>(`/cards/${cardId}/attachments`, body),
    upload: (cardId: string, file: File) => {
      const form = new FormData();
      form.set("file", file);
      return call<Attachment>("POST", `/cards/${cardId}/attachments`, { form });
    },
    remove: (id: string) => del<null>(`/attachments/${id}`),
    freshUrl: (id: string) => get<{ file_url: string | null; expires_at: string | null }>(`/attachments/${id}/url`),
  },
  categories: {
    listForBoard: (boardId: string) => get<Category[]>(`/boards/${boardId}/categories`),
    create: (boardId: string, body: { name: string; color?: string | null }) =>
      post<Category>(`/boards/${boardId}/categories`, body),
    update: (id: string, body: { name?: string; color?: string | null }) => patch<Category>(`/categories/${id}`, body),
    remove: (id: string) => del<null>(`/categories/${id}`),
  },
  comments: {
    list: (cardId: string, sort: "latest" | "popular") => get<Comment[]>(`/cards/${cardId}/comments`, { sort }),
    create: (cardId: string, content: string) => post<Comment>(`/cards/${cardId}/comments`, { content }),
    reply: (commentId: string, content: string) => post<Comment>(`/comments/${commentId}/replies`, { content }),
    togglePriority: (id: string) => patch<Comment>(`/comments/${id}/priority`),
  },
  notifications: {
    inbox: (page: PageQuery = {}) => get<Inbox>("/notifications", pageQuery(page)),
    markRead: (id: string) => patch<Notification>(`/notifications/${id}/read`),
    readAll: () => patch<null>("/notifications/read-all"),
  },
  analytics: {
    board: (id: string) => get<Analytics>(`/boards/${id}/analytics`),
    all: () => get<Analytics[]>("/analytics/boards"),
  },
  users: {
    list: () => get<(User & { role: string })[]>("/users"),
    create: (body: { full_name: string; login_identifier: string; password: string; role: string }) =>
      post<User>("/users", body),
    update: (id: string, body: { full_name?: string; login_identifier?: string; role?: string }) =>
      patch<User>(`/users/${id}`, body),
  },
};

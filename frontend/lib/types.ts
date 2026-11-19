export type Role = "member" | "supervisor" | "manager" | "admin";
export type Priority = "high" | "medium" | "low";

export interface User {
  id: string;
  full_name: string;
  login_identifier: string;
  avatar_url: string | null;
  role?: Role;
}

export interface AuthResult {
  user: User;
  token: string;
}

export interface Column {
  id: string;
  board_id: string;
  name: string;
  order: number;
}

export interface Board {
  id: string;
  name: string;
  visibility: "public" | "private";
  owner_id: string | null;
  archived_at: string | null;
  columns?: Column[];
}

export interface Subtask {
  id: string;
  card_id: string;
  title: string;
  is_done: boolean;
  order: number;
}

export interface Attachment {
  id: string;
  card_id: string;
  name: string;
  mime_type: string | null;
  url: string | null;
  file_url: string | null;
  expires_at: string | null;
}

export interface Comment {
  id: string;
  card_id: string;
  author_id: string;
  parent_id: string | null;
  content: string;
  is_priority: boolean;
  reply_count: number;
  created_at: string;
  can_create_card: boolean;
  replies?: Comment[];
}

export interface ActivityEntry {
  id: string;
  actor_id: string;
  action: string;
  target_type: string;
  target_id: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface Card {
  id: string;
  column_id: string;
  category_id: string | null;
  assignee_id: string | null;
  title: string;
  description: string | null;
  priority: Priority;
  start_date: string | null;
  end_date: string | null;
  order: number;
  archived_at: string | null;
  subtasks: Subtask[];
  attachments: Attachment[];
  /** Absent for Guests: absence of the field is the access control. */
  comments?: Comment[];
  activity?: ActivityEntry[];
}

export interface Category {
  id: string;
  board_id: string;
  name: string;
  color: string | null;
}

export interface Notification {
  id: string;
  type: "assigned" | "deadline";
  card_id: string;
  is_read: boolean;
  notify_date: string;
  created_at: string | null;
}

export interface Inbox {
  items: Notification[];
  unread_count: number;
}

export interface Analytics {
  board_id: string;
  name: string;
  total: number;
  done: number;
  in_progress: number;
  overdue: number;
  done_delta: number;
}

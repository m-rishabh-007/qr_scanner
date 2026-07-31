export type Tokens = { access: string; refresh: string };
export type LoginResponse = Tokens & { user: { email: string; business_name: string } };

export type DomainOption = { id: number; slug: string; name: string };
export type Location = {
  id: number;
  name: string;
  domain: DomainOption;
  google_review_url: string;
  google_link_verified_at: string | null;
  public_qr_token: string;
  active: boolean;
  default_language: string;
  logo_url: string;
  public_url: string;
  qr_png_url: string;
};

export type Overview = {
  period_days: 7 | 30 | 90;
  response_count: number;
  metrics: {
    qr_scans: number;
    feedback_completed: number;
    generation_succeeded: number;
    draft_selections: number;
    google_page_opened: number;
    feedback_completion_rate: number | null;
    google_open_rate: number | null;
    average_overall_score: number | null;
  };
  trend: { day: string; average: number; responses: number }[];
  aspects: { aspect_id: string; label: string; average: number; responses: number }[];
  highlights: { type: string; text: string }[];
};

export type FeedbackItem = {
  id: number;
  created_at: string;
  submitted_at: string | null;
  overall_rating: number | null;
  optional_comment: string;
  answers: { aspect_id: string; label: string; rating: number }[];
  selected_draft_style: string | null;
  final_review_text: string;
  google_opened: boolean;
  classification: "high-rated" | "neutral" | "low-rated" | "unrated";
  language: string;
};

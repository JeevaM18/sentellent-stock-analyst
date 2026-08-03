const API_BASE_URL =
  typeof window !== "undefined"
    ? "/api"
    : process.env.BACKEND_INTERNAL_URL
    ? `${process.env.BACKEND_INTERNAL_URL}/api`
    : "http://localhost:8000/api";

export interface CompanyFundamentals {
  current_price?: number;
  market_cap?: number;
  pe_ratio?: number;
  price_to_book?: number;
  eps?: number;
  roe?: number;
  debt_to_equity?: number;
  dividend_yield?: number;
  beta?: number;
  fifty_two_week_high?: number;
  fifty_two_week_low?: number;
}

export interface Company {
  id: string;
  company_name: string;
  ticker: string;
  exchange: string;
  sector?: string;
  industry?: string;
  is_active?: boolean;
  fundamentals?: CompanyFundamentals;
}

export interface CompanyNewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  source_url: string;
  published_at?: string;
  sentiment: string;
}

export interface MarketIndexItem {
  name: string;
  price: number;
  change_percent: number;
}

export interface MarketIndicesResponse {
  nifty50: MarketIndexItem;
  sp500: MarketIndexItem;
  nasdaq: MarketIndexItem;
  india_vix: MarketIndexItem;
}

export interface MarketMoodResponse {
  score: number;
  label: string;
  description: string;
}

export interface SystemStatsResponse {
  total_companies: number;
  news_chunks: number;
  embeddings: number;
  agent_status: string;
  llm_status: string;
  latency_ms: number;
}

export interface PaginatedCompaniesResponse {
  total: number;
  page: number;
  limit: number;
  companies: Company[];
}

export interface AgentChatResponse {
  answer: string;
  conversation_id: string;
  status?: string;
  retry_after?: number;
  intent: string;
  confidence: number;
  reasoning: string[];
  tools_used: string[];
  tool_results: Record<string, unknown>;
  citations: Array<{
    title?: string;
    similarity?: number;
    source_url?: string;
    source_title?: string;
    content?: string;
  }>;
  execution_time_ms: number;
  metadata: Record<string, unknown>;
}

export interface RetrievalChunk {
  chunk_id: string;
  document_id: string;
  company_id?: string;
  ticker?: string;
  company_name?: string;
  similarity: number;
  content: string;
  chunk_index: number;
  source_title?: string;
  source_url?: string;
  published_at?: string;
}

export interface RetrievalSearchResponse {
  query: string;
  total: number;
  duration_ms: number;
  chunks: RetrievalChunk[];
}

export interface RecommendationReason {
  title: string;
  description: string;
  category: string;
}

export interface RecommendationItem {
  company_name: string;
  ticker: string;
  exchange: string;
  overall_score: number;
  confidence: number;
  fundamental_score: number;
  news_score: number;
  memory_score: number;
  portfolio_score: number;
  trend_score: number;
  reasons: RecommendationReason[];
  risk_level: string;
  expected_horizon: string;
}

export interface RecommendationResponse {
  explanation: string;
  recommendations: RecommendationItem[];
  total_candidates: number;
  execution_time_ms: number;
  confidence: number;
  citations: Array<Record<string, unknown>>;
  metadata: Record<string, unknown>;
}

export interface InvestorMemory {
  risk_profile?: string;
  investment_horizon?: string;
  preferred_sectors?: string[];
  avoided_sectors?: string[];
  investment_style?: string;
  memory_summary?: string;
  memory_facts?: string[];
  confidence_score?: number;
}

export interface WatchlistItem {
  id?: string;
  company_id: string;
  ticker: string;
  company_name: string;
  exchange: string;
  sector?: string;
  followed_at?: string;
  following?: boolean;
  company?: Company;
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  profile_picture?: string;
  created?: boolean;
}

let activeAuthToken = "dev-sentellent-auth-token";

export function setAuthToken(token: string | null | undefined) {
  if (token) {
    activeAuthToken = token;
  } else {
    activeAuthToken = "dev-sentellent-auth-token";
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  // Strip leading '/api' if API_BASE_URL already contains '/api'
  const url = API_BASE_URL.endsWith("/api") && cleanEndpoint.startsWith("/api/")
    ? `${API_BASE_URL.slice(0, -4)}${cleanEndpoint}`
    : `${API_BASE_URL}${cleanEndpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${activeAuthToken}`,
    ...(options.headers as Record<string, string>),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText || response.statusText}`);
  }

  return response.json() as Promise<T>;
}

// System Health API Service
export const SystemService = {
  getStats: () => request<SystemStatsResponse>("/api/system/stats"),
};

// Market Data API Service
export const MarketService = {
  getIndices: () => request<MarketIndicesResponse>("/api/market/indices"),
  getMood: () => request<MarketMoodResponse>("/api/market/mood"),
};

// News API Service
export const NewsService = {
  getLatest: (limit: number = 5) => request<CompanyNewsItem[]>(`/api/news/latest?limit=${limit}`),
  ingest: (ticker: string) =>
    request<{
      success: boolean;
      ticker: string;
      company_name: string;
      processed: number;
      created: number;
      message: string;
    }>("/api/news/ingest", {
      method: "POST",
      body: JSON.stringify({ ticker }),
    }),
};

// Company API Service
export const CompanyService = {
  list: (params: { search?: string; sector?: string; exchange?: string; page?: number; limit?: number } = {}) => {
    const query = new URLSearchParams();
    if (params.search) query.append("search", params.search);
    if (params.sector) query.append("sector", params.sector);
    if (params.exchange) query.append("exchange", params.exchange);
    if (params.page) query.append("page", params.page.toString());
    if (params.limit) query.append("limit", params.limit.toString());
    const queryString = query.toString() ? `?${query.toString()}` : "";
    return request<PaginatedCompaniesResponse>(`/api/companies${queryString}`);
  },

  getByTicker: (ticker: string) =>
    request<Company>(`/api/companies/ticker/${encodeURIComponent(ticker.toUpperCase())}`),

  getNews: (ticker: string, limit: number = 5) =>
    request<CompanyNewsItem[]>(`/api/companies/ticker/${encodeURIComponent(ticker.toUpperCase())}/news?limit=${limit}`),

  getSectors: () => request<string[]>("/api/companies/sectors"),
  getExchanges: () => request<string[]>("/api/companies/exchanges"),
};

// Agentic AI Research Service
export const AgentService = {
  sendQuestion: (question: string, conversationId?: string) =>
    request<AgentChatResponse>("/api/agent/chat", {
      method: "POST",
      body: JSON.stringify({ question, conversation_id: conversationId }),
    }),
};

// Semantic Retrieval Service
export const RetrievalService = {
  search: (query: string, top_k: number = 5, min_similarity: number = 0.5) =>
    request<RetrievalSearchResponse>("/api/retrieval/search", {
      method: "POST",
      body: JSON.stringify({ query, top_k, min_similarity }),
    }),
};

// Recommendation Engine Service
export const RecommendationService = {
  get: (top_k: number = 5, sector?: string, include_watchlist: boolean = true) =>
    request<RecommendationResponse>("/api/recommendations", {
      method: "POST",
      body: JSON.stringify({ top_k, sector, include_watchlist }),
    }),
};

// Watchlist Service
export const WatchlistService = {
  list: () => request<{ items: WatchlistItem[] }>("/api/watchlist"),
  follow: (companyId: string) =>
    request<{ message: string; watchlist_item: WatchlistItem }>("/api/watchlist/follow", {
      method: "POST",
      body: JSON.stringify({ company_id: companyId }),
    }),
  unfollow: (companyId: string) =>
    request<{ message: string }>(`/api/watchlist/unfollow/${companyId}`, {
      method: "DELETE",
    }),
};

// Investor Memory Service
export const MemoryService = {
  get: () => request<InvestorMemory>("/api/memory"),
  update: (data: Partial<InvestorMemory>) =>
    request<InvestorMemory>("/api/memory", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

// Auth Service
export const AuthService = {
  getMe: () => request<UserResponse>("/api/auth/me"),
  sync: (payload: { email: string; name: string; profile_picture?: string }) =>
    request<UserResponse>("/api/auth/sync", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  demoLogin: (demoUser: string) =>
    request<UserResponse>("/api/auth/demo-login", {
      method: "POST",
      body: JSON.stringify({ demo_user: demoUser }),
    }),
};

// Backward-compatible fallback api object
export const api = {
  getCompanies: () => CompanyService.list().then((res) => res.companies),
  getCompany: (ticker: string) => CompanyService.getByTicker(ticker),
  sendAgentMessage: (message: string, conversationId?: string) => AgentService.sendQuestion(message, conversationId),
  searchKnowledge: (query: string, top_k?: number) => RetrievalService.search(query, top_k),
  getRecommendations: (body: { top_k?: number; sector?: string; include_watchlist?: boolean }) =>
    RecommendationService.get(body.top_k || 5, body.sector, body.include_watchlist),
  getWatchlist: () => WatchlistService.list().then((res) => res.items.map((i) => i.company!)),
  getMemory: () => MemoryService.get(),
  updateMemory: (data: Partial<InvestorMemory>) => MemoryService.update(data),
};

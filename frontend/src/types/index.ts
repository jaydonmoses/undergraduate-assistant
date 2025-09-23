// Types for the Undergraduate Assistant app

export interface UserInfo {
  name: string;
  major: string;
  research_interests: string[];
  skills: string[];
}

export interface UserResponse extends UserInfo {
  user_id: number;
}

export interface ProfessorInfo {
  name: string;
  title: string;
  position: string;
  research_interests: string[];
  location: string;
  email?: string;
  phone?: string;
  personal_website?: string;
  google_scholar?: string;
}

export interface ProfessorRecommendationRequest {
  user_info: UserInfo;
}

export interface ProfessorRecommendationResponse {
  recommendations: ProfessorInfo[];
  match_count: number;
}

export interface ApiError {
  detail: string;
}

export interface ResearchAreasResponse {
  research_areas: string[];
  count: number;
}
// API service for communicating with the FastAPI backend

import {
  UserInfo,
  UserResponse,
  ProfessorRecommendationRequest,
  ProfessorRecommendationResponse,
  ProfessorInfo,
  ApiError
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

class ApiService {
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        detail: `HTTP error! status: ${response.status}`
      }));
      throw new Error(errorData.detail);
    }
    return response.json();
  }

  // Create or update user information
  async createUser(userInfo: UserInfo): Promise<UserResponse> {
    const response = await fetch(`${API_BASE_URL}/user_info`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userInfo),
    });

    return this.handleResponse<UserResponse>(response);
  }

  // Get user information by ID
  async getUser(userId: number): Promise<UserResponse> {
    const response = await fetch(`${API_BASE_URL}/user_info/${userId}`);
    return this.handleResponse<UserResponse>(response);
  }

  // Get professor recommendations based on user information
  async getProfessorRecommendations(
    userInfo: UserInfo
  ): Promise<ProfessorRecommendationResponse> {
    const requestData: ProfessorRecommendationRequest = { user_info: userInfo };
    
    const response = await fetch(`${API_BASE_URL}/prof_info`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    return this.handleResponse<ProfessorRecommendationResponse>(response);
  }

  // Search professors by research area, location, or name
  async searchProfessors(params: {
    research_area?: string;
    location?: string;
    name?: string;
  }): Promise<ProfessorInfo[]> {
    const searchParams = new URLSearchParams();
    
    if (params.research_area) {
      searchParams.append('research_area', params.research_area);
    }
    if (params.location) {
      searchParams.append('location', params.location);
    }
    if (params.name) {
      searchParams.append('name', params.name);
    }

    const response = await fetch(
      `${API_BASE_URL}/professors/search?${searchParams.toString()}`
    );
    
    return this.handleResponse<ProfessorInfo[]>(response);
  }

  // Get all professors with pagination
  async getAllProfessors(limit: number = 50, offset: number = 0): Promise<ProfessorInfo[]> {
    const response = await fetch(
      `${API_BASE_URL}/professors?limit=${limit}&offset=${offset}`
    );
    
    return this.handleResponse<ProfessorInfo[]>(response);
  }

  // Check if API is healthy
  async healthCheck(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/`);
    return this.handleResponse(response);
  }

  // Get all available research areas
  async getResearchAreas(): Promise<{ research_areas: string[], count: number }> {
    const response = await fetch(`${API_BASE_URL}/research-areas`);
    return this.handleResponse<{ research_areas: string[], count: number }>(response);
  }
}

export const apiService = new ApiService();
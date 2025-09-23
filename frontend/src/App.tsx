// Main App component - Orchestrates the flow: User Input -> Database -> Professor Display
import React, { useState } from 'react';
import { UserInfoForm } from './components/UserInfoForm';
import { ProfessorDisplay } from './components/ProfessorDisplay';
import { apiService } from './services/api';
import { UserInfo, ProfessorInfo } from './types';
import './App.css';

type AppState = 'form' | 'loading' | 'results' | 'error';

function App() {
  const [state, setState] = useState<AppState>('form');
  const [professors, setProfessors] = useState<ProfessorInfo[]>([]);
  const [error, setError] = useState<string>('');
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);

  const handleUserSubmit = async (userData: UserInfo) => {
    setState('loading');
    setError('');
    setUserInfo(userData);

    try {
      // Get professor recommendations from the API
      const response = await apiService.getProfessorRecommendations(userData);
      
      if (response.recommendations.length === 0) {
        setProfessors([]);
        setState('results');
      } else {
        setProfessors(response.recommendations);
        setState('results');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setState('error');
    }
  };

  const handleBack = () => {
    setState('form');
    setError('');
    setProfessors([]);
  };

  const handleRetry = () => {
    if (userInfo) {
      handleUserSubmit(userInfo);
    } else {
      setState('form');
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>Undergraduate Assistant</h1>
          <p>Connect with Khoury College professors based on your research interests</p>
        </div>
      </header>

      <main className="app-main">
        {state === 'form' && (
          <UserInfoForm onSubmit={handleUserSubmit} />
        )}
        
        {state === 'loading' && (
          <ProfessorDisplay 
            professors={[]} 
            loading={true} 
            onBack={handleBack}
          />
        )}
        
        {state === 'results' && (
          <ProfessorDisplay 
            professors={professors} 
            onBack={handleBack}
          />
        )}
        
        {state === 'error' && (
          <ProfessorDisplay 
            professors={[]} 
            error={error} 
            onBack={handleRetry}
          />
        )}
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p>&copy; 2025 Undergraduate Assistant - Khoury College of Computer Sciences</p>
          <p>Built to help students connect with faculty for research opportunities</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

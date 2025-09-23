// ProfessorDisplay component - Displays prof-info from API
import React from 'react';
import { ProfessorInfo } from '../types';
import './ProfessorDisplay.css';

interface ProfessorDisplayProps {
  professors: ProfessorInfo[];
  loading?: boolean;
  error?: string;
  onBack?: () => void;
}

export const ProfessorDisplay: React.FC<ProfessorDisplayProps> = ({
  professors,
  loading = false,
  error,
  onBack
}) => {
  if (loading) {
    return (
      <div className="professor-display-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Finding the best professor matches for you...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="professor-display-container">
        <div className="error-state">
          <h2>Oops! Something went wrong</h2>
          <p>{error}</p>
          {onBack && (
            <button onClick={onBack} className="back-button">
              Try Again
            </button>
          )}
        </div>
      </div>
    );
  }

  if (professors.length === 0) {
    return (
      <div className="professor-display-container">
        <div className="no-results">
          <h2>No Professors Found</h2>
          <p>We couldn't find any professors matching your research interests.</p>
          <p>Try adjusting your research interests or contact the admissions office for more help.</p>
          {onBack && (
            <button onClick={onBack} className="back-button">
              Update Interests
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="professor-display-container">
      <div className="professor-display">
        <div className="results-header">
          <h2>Professor Recommendations</h2>
          <p className="results-count">
            Found {professors.length} professor{professors.length !== 1 ? 's' : ''} 
            {professors.length > 0 && ' matching your profile'}
          </p>
          {onBack && (
            <button onClick={onBack} className="back-button-small">
              ← Update Information
            </button>
          )}
        </div>

        <div className="professors-grid">
          {professors.map((professor, index) => (
            <div key={index} className="professor-card">
              <div className="professor-header">
                <h3 className="professor-name">{professor.name}</h3>
                <p className="professor-title">{professor.title}</p>
                <p className="professor-position">{professor.position}</p>
              </div>

              <div className="professor-details">
                {/* Research Interests */}
                <div className="detail-section">
                  <h4>Research Interests</h4>
                  <div className="research-interests">
                    {professor.research_interests.slice(0, 5).map((interest, idx) => (
                      <span key={idx} className="interest-tag">
                        {interest}
                      </span>
                    ))}
                    {professor.research_interests.length > 5 && (
                      <span className="interest-tag more">
                        +{professor.research_interests.length - 5} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Location */}
                <div className="detail-section">
                  <h4>Location</h4>
                  <p className="location">{professor.location}</p>
                </div>

                {/* Contact Information */}
                <div className="contact-section">
                  <h4>Contact Information</h4>
                  <div className="contact-details">
                    {professor.email && (
                      <div className="contact-item">
                        <span className="contact-label">Email:</span>
                        <a href={`mailto:${professor.email}`} className="contact-link">
                          {professor.email}
                        </a>
                      </div>
                    )}
                    
                    {professor.phone && (
                      <div className="contact-item">
                        <span className="contact-label">Phone:</span>
                        <a href={`tel:${professor.phone}`} className="contact-link">
                          {professor.phone}
                        </a>
                      </div>
                    )}

                    {professor.personal_website && (
                      <div className="contact-item">
                        <span className="contact-label">Website:</span>
                        <a 
                          href={professor.personal_website} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="contact-link"
                        >
                          Personal Website
                        </a>
                      </div>
                    )}

                    {professor.google_scholar && (
                      <div className="contact-item">
                        <span className="contact-label">Scholar:</span>
                        <a 
                          href={professor.google_scholar} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="contact-link"
                        >
                          Google Scholar
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="professor-actions">
                {professor.email && (
                  <button 
                    className="action-button primary"
                    onClick={() => window.location.href = `mailto:${professor.email}?subject=Research Opportunity Inquiry`}
                  >
                    Contact Professor
                  </button>
                )}
                
                {professor.personal_website && (
                  <button 
                    className="action-button secondary"
                    onClick={() => window.open(professor.personal_website, '_blank')}
                  >
                    View Profile
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Additional Actions */}
        <div className="additional-actions">
          <p className="tip">
            💡 <strong>Tip:</strong> When reaching out, mention specific research interests that align with your goals!
          </p>
        </div>
      </div>
    </div>
  );
};
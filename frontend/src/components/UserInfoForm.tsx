// UserInfoForm component - Collects user data from user input
import React, { useState, useEffect } from 'react';
import { UserInfo } from '../types';
import { apiService } from '../services/api';
import './UserInfoForm.css';

interface UserInfoFormProps {
  onSubmit: (userInfo: UserInfo) => void;
  loading?: boolean;
}

export const UserInfoForm: React.FC<UserInfoFormProps> = ({ onSubmit, loading = false }) => {
  const [formData, setFormData] = useState<UserInfo>({
    name: '',
    major: '',
    research_interests: [],
    skills: []
  });

  const [currentInterest, setCurrentInterest] = useState('');
  const [currentSkill, setCurrentSkill] = useState('');
  const [availableResearchAreas, setAvailableResearchAreas] = useState<string[]>([]);
  const [filteredResearchAreas, setFilteredResearchAreas] = useState<string[]>([]);
  const [showResearchDropdown, setShowResearchDropdown] = useState(false);
  const [loadingResearchAreas, setLoadingResearchAreas] = useState(true);

  // Fetch available research areas on component mount
  useEffect(() => {
    const fetchResearchAreas = async () => {
      try {
        const response = await apiService.getResearchAreas();
        setAvailableResearchAreas(response.research_areas);
        setFilteredResearchAreas(response.research_areas);
      } catch (error) {
        console.error('Failed to fetch research areas:', error);
        // Fallback to some common research areas if API fails
        const fallbackAreas = [
          'Artificial Intelligence',
          'Machine Learning',
          'Data Science',
          'Computer Vision',
          'Natural Language Processing',
          'Cybersecurity',
          'Software Engineering',
          'Human-Computer Interaction',
          'Robotics',
          'Computer Networks'
        ];
        setAvailableResearchAreas(fallbackAreas);
        setFilteredResearchAreas(fallbackAreas);
      } finally {
        setLoadingResearchAreas(false);
      }
    };

    fetchResearchAreas();
  }, []);

  // Filter research areas based on input
  const filterResearchAreas = (input: string) => {
    if (!input.trim()) {
      setFilteredResearchAreas(availableResearchAreas);
      return;
    }
    
    const filtered = availableResearchAreas.filter(area =>
      area.toLowerCase().includes(input.toLowerCase())
    );
    setFilteredResearchAreas(filtered);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('.autocomplete-container')) {
        setShowResearchDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (field: keyof UserInfo, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addResearchInterest = (interest?: string) => {
    const interestToAdd = interest || currentInterest;
    if (interestToAdd.trim() && !formData.research_interests.includes(interestToAdd.trim())) {
      setFormData(prev => ({
        ...prev,
        research_interests: [...prev.research_interests, interestToAdd.trim()]
      }));
      setCurrentInterest('');
      setShowResearchDropdown(false);
    }
  };

  const handleResearchInputChange = (value: string) => {
    setCurrentInterest(value);
    filterResearchAreas(value);
    setShowResearchDropdown(true);
  };

  const handleResearchInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addResearchInterest();
    } else if (e.key === 'Escape') {
      setShowResearchDropdown(false);
    }
  };

  const removeResearchInterest = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      research_interests: prev.research_interests.filter(i => i !== interest)
    }));
  };

  const addSkill = () => {
    if (currentSkill.trim() && !formData.skills.includes(currentSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, currentSkill.trim()]
      }));
      setCurrentSkill('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name && formData.major) { // Remove requirement for research interests
      onSubmit(formData);
    }
  };

  const isFormValid = formData.name && formData.major; // Remove research interests requirement

  return (
    <div className="user-info-form-container">
      <div className="user-info-form">
        <h2>Tell Us About Yourself</h2>
        <p className="form-description">
          Enter your information to get personalized professor recommendations
        </p>

        <form onSubmit={handleSubmit}>
          {/* Name Input */}
          <div className="form-group">
            <label htmlFor="name">Full Name *</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Enter your full name"
              required
            />
          </div>

          {/* Major Input */}
          <div className="form-group">
            <label htmlFor="major">Major *</label>
            <select
              id="major"
              value={formData.major}
              onChange={(e) => handleInputChange('major', e.target.value)}
              required
            >
              <option value="">Select your major</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Data Science">Data Science</option>
              <option value="Information Systems">Information Systems</option>
              <option value="Cybersecurity">Cybersecurity</option>
              <option value="Computer Engineering">Computer Engineering</option>
              <option value="Game Design">Game Design</option>
              <option value="Human-Computer Interaction">Human-Computer Interaction</option>
              <option value="Artificial Intelligence">Artificial Intelligence</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Research Interests */}
          <div className="form-group">
            <label>Research Interests {loadingResearchAreas && <span className="loading-text">(Loading options...)</span>}</label>
            <div className="tag-input-container">
              <div className="tag-input autocomplete-container">
                <input
                  type="text"
                  value={currentInterest}
                  onChange={(e) => handleResearchInputChange(e.target.value)}
                  onKeyPress={handleResearchInputKeyPress}
                  onFocus={() => setShowResearchDropdown(true)}
                  placeholder="Start typing or select research interests (optional)"
                  disabled={loadingResearchAreas}
                />
                <button 
                  type="button" 
                  onClick={() => addResearchInterest()} 
                  disabled={!currentInterest.trim() || loadingResearchAreas}
                >
                  Add
                </button>
                
                {/* Dropdown for autocomplete */}
                {showResearchDropdown && filteredResearchAreas.length > 0 && currentInterest && (
                  <div className="autocomplete-dropdown">
                    {filteredResearchAreas.slice(0, 10).map((area, index) => (
                      <div
                        key={index}
                        className="autocomplete-item"
                        onClick={() => addResearchInterest(area)}
                      >
                        {area}
                      </div>
                    ))}
                    {filteredResearchAreas.length > 10 && (
                      <div className="autocomplete-item disabled">
                        ... and {filteredResearchAreas.length - 10} more options
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="tags">
                {formData.research_interests.map((interest, index) => (
                  <span key={index} className="tag">
                    {interest}
                    <button
                      type="button"
                      onClick={() => removeResearchInterest(interest)}
                      className="tag-remove"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Skills */}
          <div className="form-group">
            <label>Skills</label>
            <div className="tag-input-container">
              <div className="tag-input">
                <input
                  type="text"
                  value={currentSkill}
                  onChange={(e) => setCurrentSkill(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  placeholder="Add skills (e.g., Python, JavaScript)"
                />
                <button type="button" onClick={addSkill} disabled={!currentSkill.trim()}>
                  Add
                </button>
              </div>
              <div className="tags">
                {formData.skills.map((skill, index) => (
                  <span key={index} className="tag">
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="tag-remove"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button 
            type="submit" 
            className="submit-button"
            disabled={!isFormValid || loading}
          >
            {loading ? 'Finding Professors...' : 'Get Professor Recommendations'}
          </button>
        </form>
      </div>
    </div>
  );
};
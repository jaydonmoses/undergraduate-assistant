import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
import os


class UndergraduateAssistantDatabase:
    """Database class for managing users and professors data"""
    
    def __init__(self, db_path: str = "data/undergraduate_assistant.db"):
        # Convert relative path to absolute path based on backend directory
        if not os.path.isabs(db_path):
            # Get the directory where this database.py file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to backend directory, then to data
            backend_dir = os.path.dirname(current_dir)
            db_path = os.path.join(backend_dir, db_path)
        
        self.db_path = db_path
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with users and professors tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table for user input
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                major TEXT NOT NULL,
                research_interests TEXT,  -- JSON string for list storage
                skills TEXT,  -- JSON string for list storage
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create professors table for web scraper data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS professors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                title TEXT,
                position TEXT,
                research_interests TEXT,  -- JSON string for list storage
                location TEXT,
                email TEXT,
                phone TEXT,
                personal_website TEXT,
                google_scholar TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better query performance
        # Users table indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_major ON users(major)')
        
        # Professors table indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_professors_name ON professors(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_professors_email ON professors(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_professors_location ON professors(location)')
        
        conn.commit()
        conn.close()
    
    def dict_factory(self, cursor, row):
        """Convert database row to dictionary"""
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}
    
    # =================== USERS TABLE METHODS ===================
    
    def insert_user(self, user_data: Dict) -> int:
        """Insert a new user into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert lists to JSON strings
        research_interests_json = json.dumps(user_data.get('research_interests', []))
        skills_json = json.dumps(user_data.get('skills', []))
        
        cursor.execute('''
            INSERT INTO users (name, major, research_interests, skills)
            VALUES (?, ?, ?, ?)
        ''', (
            user_data.get('name'),
            user_data.get('major'),
            research_interests_json,
            skills_json
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id
    
    def get_all_users(self) -> List[Dict]:
        """Get all users from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = self.dict_factory
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY name')
        users = cursor.fetchall()
        
        # Parse JSON fields back to lists
        for user in users:
            user['research_interests'] = json.loads(user['research_interests'] or '[]')
            user['skills'] = json.loads(user['skills'] or '[]')
        
        conn.close()
        return users
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get a user by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = self.dict_factory
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            user['research_interests'] = json.loads(user['research_interests'] or '[]')
            user['skills'] = json.loads(user['skills'] or '[]')
        
        conn.close()
        return user
    
    def search_users(self, name: str = None, major: str = None, 
                    research_interest: str = None, skill: str = None,
                    limit: int = 100, offset: int = 0) -> List[Dict]:
        """Search users by various criteria with pagination"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = self.dict_factory
        cursor = conn.cursor()
        
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if major:
            query += " AND major LIKE ?"
            params.append(f"%{major}%")
        
        if research_interest:
            query += " AND research_interests LIKE ?"
            params.append(f"%{research_interest}%")
        
        if skill:
            query += " AND skills LIKE ?"
            params.append(f"%{skill}%")
        
        query += " ORDER BY name LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        # Parse JSON fields back to lists
        for user in users:
            user['research_interests'] = json.loads(user['research_interests'] or '[]')
            user['skills'] = json.loads(user['skills'] or '[]')
        
        conn.close()
        return users
    
    def update_user(self, user_id: int, user_data: Dict) -> bool:
        """Update a user's information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert lists to JSON strings
        research_interests_json = json.dumps(user_data.get('research_interests', []))
        skills_json = json.dumps(user_data.get('skills', []))
        
        cursor.execute('''
            UPDATE users 
            SET name = ?, major = ?, research_interests = ?, skills = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            user_data.get('name'),
            user_data.get('major'),
            research_interests_json,
            skills_json,
            user_id
        ))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    # =================== PROFESSORS TABLE METHODS ===================
    
    def insert_professor(self, prof_data: Dict) -> int:
        """Insert a single professor into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert research_interests list to JSON string
        research_interests_json = json.dumps(prof_data.get('research_interests', []))
        
        cursor.execute('''
            INSERT INTO professors (
                name, title, position, research_interests, location, 
                email, phone, personal_website, google_scholar
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prof_data.get('name'),
            prof_data.get('title'),
            prof_data.get('position'),
            research_interests_json,
            prof_data.get('location'),
            prof_data.get('email'),
            prof_data.get('phone'),
            prof_data.get('personal_website'),
            prof_data.get('google_scholar')
        ))
        
        professor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return professor_id
    
    def get_all_professors(self) -> List[Dict]:
        """Get all professors from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = self.dict_factory
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM professors ORDER BY name')
        professors = cursor.fetchall()
        
        # Parse JSON fields back to lists
        for prof in professors:
            prof['research_interests'] = json.loads(prof['research_interests'] or '[]')
        
        conn.close()
        return professors
    
    def get_professor_by_id(self, professor_id: int) -> Optional[Dict]:
        """Get a professor by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = self.dict_factory
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM professors WHERE id = ?', (professor_id,))
        professor = cursor.fetchone()
        
        if professor:
            professor['research_interests'] = json.loads(professor['research_interests'] or '[]')
        
        conn.close()
        return professor
    
    def search_professors(self, name: str = None, location: str = None, 
                         research_area: str = None, title: str = None,
                         limit: int = 100, offset: int = 0) -> List[Dict]:
        """Search professors by various criteria with pagination"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = self.dict_factory
        cursor = conn.cursor()
        
        query = "SELECT * FROM professors WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        if research_area:
            query += " AND research_interests LIKE ?"
            params.append(f"%{research_area}%")
        
        if title:
            query += " AND title LIKE ?"
            params.append(f"%{title}%")
        
        query += " ORDER BY name LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        professors = cursor.fetchall()
        
        # Parse JSON fields back to lists
        for prof in professors:
            prof['research_interests'] = json.loads(prof['research_interests'] or '[]')
        
        conn.close()
        return professors
    
    def insert_all_professors(self, professors_data: List[Dict]) -> int:
        """Insert multiple professors into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inserted_count = 0
        
        for prof_data in professors_data:
            try:
                research_interests_json = json.dumps(prof_data.get('research_interests', []))
                
                cursor.execute('''
                    INSERT INTO professors (
                        name, title, position, research_interests, location, 
                        email, phone, personal_website, google_scholar
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prof_data.get('name'),
                    prof_data.get('title'),
                    prof_data.get('position'),
                    research_interests_json,
                    prof_data.get('location'),
                    prof_data.get('email'),
                    prof_data.get('phone'),
                    prof_data.get('personal_website'),
                    prof_data.get('google_scholar')
                ))
                inserted_count += 1
                
            except Exception as e:
                print(f"Error inserting professor {prof_data.get('name', 'Unknown')}: {e}")
        
        conn.commit()
        conn.close()
        
        return inserted_count
    
    def update_professor(self, professor_id: int, prof_data: Dict) -> bool:
        """Update a professor's information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        research_interests_json = json.dumps(prof_data.get('research_interests', []))
        
        cursor.execute('''
            UPDATE professors 
            SET name = ?, title = ?, position = ?, research_interests = ?, 
                location = ?, email = ?, phone = ?, personal_website = ?, 
                google_scholar = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            prof_data.get('name'),
            prof_data.get('title'),
            prof_data.get('position'),
            research_interests_json,
            prof_data.get('location'),
            prof_data.get('email'),
            prof_data.get('phone'),
            prof_data.get('personal_website'),
            prof_data.get('google_scholar'),
            professor_id
        ))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def delete_professor(self, professor_id: int) -> bool:
        """Delete a professor from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM professors WHERE id = ?', (professor_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    # =================== UTILITY METHODS ===================
    
    def clear_users_table(self):
        """Clear all users from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users')
        conn.commit()
        conn.close()
    
    def clear_professors_table(self):
        """Clear all professors from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM professors')
        conn.commit()
        conn.close()
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user count
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        # Get professor count
        cursor.execute('SELECT COUNT(*) FROM professors')
        professor_count = cursor.fetchone()[0]
        
        # Get unique majors
        cursor.execute('SELECT DISTINCT major FROM users WHERE major IS NOT NULL')
        majors = [row[0] for row in cursor.fetchall()]
        
        # Get unique locations
        cursor.execute('SELECT DISTINCT location FROM professors WHERE location IS NOT NULL')
        locations = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_users': user_count,
            'total_professors': professor_count,
            'unique_majors': len(majors),
            'unique_locations': len(locations),
            'majors': majors,
            'locations': locations
        }
    
    def match_users_to_professors(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Find professors that match a user's research interests"""
        user = self.get_user_by_id(user_id)
        if not user:
            return []
        
        user_interests = user.get('research_interests', [])
        if not user_interests:
            return []
        
        matched_professors = []
        all_professors = self.get_all_professors()
        
        for prof in all_professors:
            prof_interests = prof.get('research_interests', [])
            # Calculate overlap between user and professor interests
            overlap = set(user_interests) & set(prof_interests)
            if overlap:
                prof['match_score'] = len(overlap)
                prof['matching_interests'] = list(overlap)
                matched_professors.append(prof)
        
        # Sort by match score (highest first) and limit results
        matched_professors.sort(key=lambda x: x['match_score'], reverse=True)
        return matched_professors[:limit]
    
    def get_popular_research_areas(self, table: str = 'professors') -> List[Dict]:
        """Get the most popular research areas from users or professors"""
        if table not in ['users', 'professors']:
            return []
        
        all_records = self.get_all_users() if table == 'users' else self.get_all_professors()
        research_count = {}
        
        for record in all_records:
            interests = record.get('research_interests', [])
            for interest in interests:
                research_count[interest] = research_count.get(interest, 0) + 1
        
        # Convert to list of dictionaries and sort by count
        popular_areas = [
            {'research_area': area, 'count': count}
            for area, count in research_count.items()
        ]
        popular_areas.sort(key=lambda x: x['count'], reverse=True)
        
        return popular_areas

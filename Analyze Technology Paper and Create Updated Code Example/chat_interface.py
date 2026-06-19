"""
Fibonacci Grid AI - Chat Interface Module

This module provides the chat interface functionality for the Fibonacci Grid AI system,
enabling users to interact with custom-trained AI models.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Optional

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.grid_ai_integration import GridAIIntegration
from backend.ai_manager import AIManager

class ChatInterface:
    """
    Chat interface for interacting with grid-powered AI models.
    
    This class provides methods for managing chat sessions, processing messages,
    and generating responses using the Fibonacci Grid System.
    """
    
    def __init__(self, ai_manager: AIManager, grid_integration: GridAIIntegration):
        """
        Initialize the chat interface.
        
        Args:
            ai_manager: AI manager instance
            grid_integration: Grid AI integration instance
        """
        self.ai_manager = ai_manager
        self.grid_integration = grid_integration
        self.chat_sessions = {}
        self.session_history = {}
    
    def create_session(self, model_id: str, user_id: str = "default_user") -> str:
        """
        Create a new chat session.
        
        Args:
            model_id: Model identifier
            user_id: User identifier
            
        Returns:
            Session identifier
        """
        # Generate session ID
        session_id = f"session_{int(time.time())}_{model_id[:8]}_{user_id[:8]}"
        
        # Create session
        self.chat_sessions[session_id] = {
            'model_id': model_id,
            'user_id': user_id,
            'created_at': int(time.time()),
            'last_activity': int(time.time()),
            'message_count': 0
        }
        
        # Initialize session history
        self.session_history[session_id] = []
        
        # Add system welcome message
        model_info = self.ai_manager.model_manager.get_model(model_id)
        model_name = model_info.get('metadata', {}).get('name', model_info.get('filename', 'AI Assistant'))
        
        welcome_message = {
            'role': 'system',
            'content': f"Welcome to your chat with {model_name}, powered by the Fibonacci Grid System. This model uses advanced grid-based compression and pattern recognition to provide efficient and insightful responses.",
            'timestamp': int(time.time())
        }
        
        self.session_history[session_id].append(welcome_message)
        
        return session_id
    
    def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Send a message to the model and get a response.
        
        Args:
            session_id: Session identifier
            message: User message
            
        Returns:
            Dictionary containing response information
        """
        # Check if session exists
        if session_id not in self.chat_sessions:
            return {'error': 'Session not found'}
        
        # Update session activity
        self.chat_sessions[session_id]['last_activity'] = int(time.time())
        self.chat_sessions[session_id]['message_count'] += 1
        
        # Add user message to history
        user_message = {
            'role': 'user',
            'content': message,
            'timestamp': int(time.time())
        }
        
        self.session_history[session_id].append(user_message)
        
        # Get model ID from session
        model_id = self.chat_sessions[session_id]['model_id']
        
        # Get chat history for context
        history = self.session_history[session_id]
        
        # Generate response using grid integration
        response_data = self.grid_integration.generate_grid_response(
            model_id=model_id,
            message=message,
            chat_history=history
        )
        
        # Add AI response to history
        ai_message = {
            'role': 'assistant',
            'content': response_data['response'],
            'timestamp': response_data['timestamp'],
            'grid_metrics': response_data.get('grid_metrics', {})
        }
        
        self.session_history[session_id].append(ai_message)
        
        return {
            'session_id': session_id,
            'response': response_data['response'],
            'timestamp': response_data['timestamp'],
            'message_id': len(self.session_history[session_id]) - 1,
            'grid_metrics': response_data.get('grid_metrics', {})
        }
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of a chat session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries
        """
        if session_id not in self.session_history:
            return []
        
        return self.session_history[session_id]
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a chat session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing session information
        """
        if session_id not in self.chat_sessions:
            return {'error': 'Session not found'}
        
        session_info = self.chat_sessions[session_id].copy()
        
        # Add message count
        session_info['message_count'] = len(self.session_history.get(session_id, []))
        
        # Get model information
        model_id = session_info['model_id']
        model_info = self.ai_manager.model_manager.get_model(model_id)
        
        if 'error' not in model_info:
            session_info['model_name'] = model_info.get('metadata', {}).get('name', model_info.get('filename', 'Unknown'))
            session_info['model_type'] = model_info.get('model_type', 'unknown')
        
        return session_info
    
    def list_sessions(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        List all chat sessions, optionally filtered by user.
        
        Args:
            user_id: Optional user identifier to filter by
            
        Returns:
            List of session information dictionaries
        """
        sessions = []
        
        for session_id, session in self.chat_sessions.items():
            if user_id is None or session['user_id'] == user_id:
                session_info = self.get_session_info(session_id)
                sessions.append(session_info)
        
        # Sort by last activity (newest first)
        sessions.sort(key=lambda s: s.get('last_activity', 0), reverse=True)
        
        return sessions
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Delete a chat session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing deletion status
        """
        if session_id not in self.chat_sessions:
            return {'error': 'Session not found'}
        
        # Get session info before deletion
        session_info = self.chat_sessions[session_id].copy()
        
        # Delete session
        del self.chat_sessions[session_id]
        
        # Delete history
        if session_id in self.session_history:
            del self.session_history[session_id]
        
        return {
            'status': 'deleted',
            'session_id': session_id,
            'model_id': session_info['model_id'],
            'user_id': session_info['user_id']
        }
    
    def analyze_chat(self, session_id: str) -> Dict[str, Any]:
        """
        Analyze a chat session using the Fibonacci Grid System.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing analysis results
        """
        if session_id not in self.session_history:
            return {'error': 'Session not found'}
        
        history = self.session_history[session_id]
        
        # Extract user messages
        user_messages = [msg['content'] for msg in history if msg['role'] == 'user']
        
        # Extract AI responses
        ai_messages = [msg['content'] for msg in history if msg['role'] == 'assistant']
        
        # Calculate basic metrics
        avg_user_length = sum(len(msg) for msg in user_messages) / len(user_messages) if user_messages else 0
        avg_ai_length = sum(len(msg) for msg in ai_messages) / len(ai_messages) if ai_messages else 0
        
        # Extract grid metrics from AI responses
        grid_metrics = [msg.get('grid_metrics', {}) for msg in history if msg['role'] == 'assistant' and 'grid_metrics' in msg]
        
        # Calculate average grid metrics
        avg_grid_metrics = {}
        if grid_metrics:
            for key in grid_metrics[0].keys():
                values = [m.get(key, 0) for m in grid_metrics if key in m]
                avg_grid_metrics[key] = sum(values) / len(values) if values else 0
        
        # Analyze conversation flow using grid patterns
        flow_analysis = self._analyze_conversation_flow(history)
        
        return {
            'session_id': session_id,
            'message_count': len(history),
            'user_message_count': len(user_messages),
            'ai_message_count': len(ai_messages),
            'avg_user_message_length': avg_user_length,
            'avg_ai_message_length': avg_ai_length,
            'avg_grid_metrics': avg_grid_metrics,
            'flow_analysis': flow_analysis,
            'timestamp': int(time.time())
        }
    
    def _analyze_conversation_flow(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze conversation flow using grid patterns.
        
        Args:
            history: Chat history
            
        Returns:
            Dictionary containing flow analysis
        """
        # This is a simplified analysis for demonstration
        # In a real system, this would use more sophisticated NLP and grid pattern analysis
        
        # Extract topics from user messages
        user_messages = [msg['content'] for msg in history if msg['role'] == 'user']
        all_words = ' '.join(user_messages).lower().split()
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                       'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'like', 
                       'from', 'of', 'as', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        filtered_words = [word for word in all_words if word not in common_words and len(word) > 3]
        
        # Count word frequencies
        word_counts = {}
        for word in filtered_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top topics
        top_topics = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Analyze sentiment (simplified)
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
                         'helpful', 'useful', 'interesting', 'impressive', 'like', 'love'}
        
        negative_words = {'bad', 'poor', 'terrible', 'awful', 'horrible', 'useless', 
                         'unhelpful', 'boring', 'disappointing', 'dislike', 'hate'}
        
        positive_count = sum(1 for word in filtered_words if word in positive_words)
        negative_count = sum(1 for word in filtered_words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        sentiment_score = (positive_count - negative_count) / total_sentiment_words if total_sentiment_words > 0 else 0
        
        return {
            'top_topics': [{'topic': topic, 'count': count} for topic, count in top_topics],
            'topic_diversity': len(word_counts) / len(filtered_words) if filtered_words else 0,
            'sentiment_score': sentiment_score,
            'conversation_depth': len(history) / 2,  # Pairs of user-AI messages
            'user_engagement': sum(len(msg) for msg in user_messages) / len(user_messages) if user_messages else 0
        }

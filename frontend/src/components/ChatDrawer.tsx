import React, { useState, useEffect, useRef } from 'react';
import { useClerk } from '@clerk/clerk-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  XMarkIcon, 
  PaperAirplaneIcon,
  UserCircleIcon,
  EllipsisHorizontalIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import './ChatDrawer.css';

interface ChatDrawerProps {
  userId: string;
  userRole: 'admin' | 'user';
  targetUserId?: string;
  onClose: () => void;
}

interface ChatUser {
  name: string;
  id: string;
  username: string;
}

interface Message {
  _id: string;
  from_id: string;
  to_id: string;
  content: string;
  timestamp: string;
}

const ChatDrawer: React.FC<ChatDrawerProps> = ({ userId, userRole, targetUserId, onClose }) => {
  const clerk = useClerk();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [pollInterval, setPollInterval] = useState<number | null>(null);
  const [adminTargetId, setAdminTargetId] = useState(targetUserId || '');
  const [userList, setUserList] = useState<ChatUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<ChatUser | null>(null);
  const [userListLoading, setUserListLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch user list for admin
  useEffect(() => {
    if (userRole === 'admin') {
      fetchUserList();
    }
  }, [userRole]);

  // Focus input when drawer opens
  useEffect(() => {
    setTimeout(() => {
      inputRef.current?.focus();
    }, 300);
  }, []);

  const fetchUserList = async () => {
    setUserListLoading(true);
    try {
      const token = await clerk.session?.getToken();
      const res = await fetch('http://127.0.0.1:5000/api/admin/users/only-users', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!res.ok) return;
      const data = await res.json();
      setUserList(data.users || []);
      if (!selectedUser && data.users && data.users.length > 0) {
        setSelectedUser(data.users[0]);
        setAdminTargetId(data.users[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch user list:', error);
    } finally {
      setUserListLoading(false);
    }
  };

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Poll for messages
  useEffect(() => {
    if (!userId || (userRole === 'admin' && !adminTargetId)) return;
    fetchMessages();
    if (pollInterval) clearInterval(pollInterval);
    const interval = window.setInterval(fetchMessages, 3000);
    setPollInterval(interval);
    return () => clearInterval(interval);
  }, [userId, userRole, adminTargetId]);

  const fetchMessages = async () => {
    try {
      const id = userRole === 'admin' ? adminTargetId : userId;
      if (!id) return;
      const token = await clerk.session?.getToken();
      const res = await fetch(`http://127.0.0.1:5000/api/chat/messages?user_id=${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!res.ok) return;
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setIsTyping(true);
    
    const tempMessage: Message = {
      _id: `temp-${Date.now()}`,
      from_id: userId,
      to_id: userRole === 'admin' ? adminTargetId : 'admin',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempMessage]);
    const messageContent = input.trim();
    setInput('');

    try {
      const payload = {
        to_id: userRole === 'admin' ? adminTargetId : 'admin',
        to_role: userRole === 'admin' ? 'user' : 'admin',
        content: messageContent,
      };
      const token = await clerk.session?.getToken();
      const res = await fetch('http://127.0.0.1:5000/api/chat/send', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setMessages(prev => prev.filter(msg => msg._id !== tempMessage._id));
        setTimeout(fetchMessages, 500);
      } else {
        setMessages(prev => prev.filter(msg => msg._id !== tempMessage._id));
        setInput(messageContent);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => prev.filter(msg => msg._id !== tempMessage._id));
      setInput(messageContent);
    } finally {
      setLoading(false);
      setIsTyping(false);
    }
  };

  const handleUserSelect = (user: ChatUser) => {
    setSelectedUser(user);
    setAdminTargetId(user.id);
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 3600);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <AnimatePresence>
      <motion.div 
        className="fixed inset-0 z-50 flex justify-end"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
      >
        {/* Overlay */}
        <motion.div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm chat-overlay" 
          onClick={onClose}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />
        
        {/* Drawer */}
        <motion.div 
          className="relative w-full sm:max-w-2xl h-full bg-white dark:bg-gray-900 shadow-2xl flex flex-col sm:flex-row chat-drawer"
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        >
          {/* User List for Admin */}
          {userRole === 'admin' && (
            <motion.div 
              className="w-full sm:w-80 border-b sm:border-b-0 sm:border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex flex-col"
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
                <div className="flex items-center gap-3">
                  <UserCircleIcon className="h-6 w-6 text-yellow-500" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Users</h3>
                  <div className="ml-auto text-sm text-gray-500 dark:text-gray-400">
                    {userList.length} online
                  </div>
                </div>
              </div>
              
              <div className="flex-1 overflow-y-auto chat-scrollbar">
                {userListLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-yellow-500 border-t-transparent"></div>
                    <span className="ml-2 text-gray-500 dark:text-gray-400">Loading users...</span>
                  </div>
                ) : userList.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    No users found
                  </div>
                ) : (
                  <div className="p-2">
                    {userList.map((user, index) => (
                      <motion.div
                        key={user.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`
                          cursor-pointer rounded-lg p-3 mb-2 transition-all duration-200 chat-user-item
                          hover:bg-white hover:shadow-sm dark:hover:bg-gray-700
                          ${selectedUser?.id === user.id 
                            ? 'bg-yellow-50 border-2 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-700' 
                            : 'bg-transparent border-2 border-transparent hover:border-gray-200 dark:hover:border-gray-600'
                          }
                        `}
                        onClick={() => handleUserSelect(user)}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`relative user-avatar ${selectedUser?.id === user.id ? 'selected' : ''}`}>
                            <UserCircleIcon className="h-10 w-10 text-gray-400" />
                            <div className="absolute bottom-0 right-0 h-3 w-3 bg-green-400 border-2 border-white rounded-full"></div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 dark:text-white truncate">
                              {user.name || user.username || 'Anonymous'}
                            </p>
                            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                              {user.username && user.name ? `@${user.username}` : user.id}
                            </p>
                          </div>
                          {selectedUser?.id === user.id && (
                            <div className="h-2 w-2 bg-yellow-400 rounded-full"></div>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Chat Panel */}
          <div className="flex-1 flex flex-col bg-white dark:bg-gray-900">
            {/* Chat Header */}
            <motion.div 
              className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center gap-3">
                <UserCircleIcon className="h-8 w-8 text-yellow-500" />
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {userRole === 'admin' 
                      ? (selectedUser?.name || selectedUser?.username || 'Select a user')
                      : '🐝 Admin Support'
                    }
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {userRole === 'admin' ? 'User Chat' : 'We\'re here to help you! (v2.0)'}
                  </p>
                </div>
              </div>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onClose}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                aria-label="Close chat"
              >
                <XMarkIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              </motion.button>
            </motion.div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-800 chat-scrollbar chat-content">
              <AnimatePresence>
                {messages.length === 0 ? (
                  <motion.div 
                    className="flex items-center justify-center h-full text-center"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    <div className="max-w-sm">
                      <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <EllipsisHorizontalIcon className="h-8 w-8 text-yellow-500" />
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                        Start a conversation
                      </h3>
                      <p className="text-gray-500 dark:text-gray-400">
                        {userRole === 'admin' 
                          ? 'Select a user from the list to start chatting'
                          : 'Send a message to get help from our admin team'
                        }
                      </p>
                    </div>
                  </motion.div>
                ) : (
                  messages.map((msg, idx) => {
                    const isOwn = msg.from_id === userId;
                    return (
                      <motion.div
                        key={msg._id}
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ delay: idx * 0.02 }}
                        className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`
                          max-w-[85%] sm:max-w-[70%] px-4 py-3 rounded-2xl shadow-sm message-bubble
                          ${isOwn 
                            ? 'bg-yellow-400 text-black rounded-br-md' 
                            : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md border border-gray-200 dark:border-gray-600'
                          }
                        `}>
                          <p className="text-sm leading-relaxed">{msg.content}</p>
                          <div className={`flex items-center justify-between text-xs mt-2 ${isOwn ? 'text-yellow-800' : 'text-gray-500 dark:text-gray-400'}`}>
                            <span>{msg.timestamp && formatTimestamp(msg.timestamp)}</span>
                            {isOwn && (
                              <div className="message-status sent">
                                <CheckCircleIcon className="h-3 w-3" />
                              </div>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </AnimatePresence>
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex justify-start"
                >
                  <div className="bg-gray-200 dark:bg-gray-600 px-4 py-3 rounded-2xl rounded-bl-md">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <motion.div 
              className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex gap-3 items-end">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    className="
                      w-full px-4 py-3 pr-12 rounded-2xl border border-gray-300 dark:border-gray-600 
                      bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white
                      focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent
                      placeholder-gray-500 dark:placeholder-gray-400
                      transition-all duration-200 chat-input
                    "
                    placeholder={
                      userRole === 'admin' && !adminTargetId 
                        ? 'Select a user to start chatting...' 
                        : 'Type your message...'
                    }
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => { 
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                    disabled={loading || (userRole === 'admin' && !adminTargetId)}
                    maxLength={500}
                  />
                  <div className="absolute right-3 bottom-3 text-xs text-gray-400 dark:text-gray-500">
                    {input.length}/500
                  </div>
                </div>
                
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={sendMessage}
                  disabled={loading || !input.trim() || (userRole === 'admin' && !adminTargetId)}
                  className="
                    bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-300 dark:disabled:bg-gray-600
                    text-black disabled:text-gray-500 dark:disabled:text-gray-400
                    p-3 rounded-2xl font-medium shadow-sm transition-all duration-200
                    disabled:cursor-not-allowed disabled:shadow-none
                    flex items-center justify-center min-w-[48px] chat-button
                  "
                  aria-label="Send message"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-current border-t-transparent"></div>
                  ) : (
                    <PaperAirplaneIcon className="h-5 w-5" />
                  )}
                </motion.button>
              </div>
              
              <div className="flex justify-between items-center mt-2 text-xs text-gray-500 dark:text-gray-400">
                <span>Press Enter to send, Shift+Enter for new line</span>
                {userRole === 'admin' && selectedUser && (
                  <span>Chatting with {selectedUser.name || selectedUser.username}</span>
                )}
              </div>
            </motion.div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ChatDrawer;

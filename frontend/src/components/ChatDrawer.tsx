import React, { useState, useEffect, useRef, useCallback} from 'react';
import { apiUrl } from '../utils/api';

interface ChatDrawerProps {
  userId: string;
  userRole: 'admin' | 'user';
  targetUserId?: string; // For admin, the user to chat with
  onClose: () => void;
}

interface ChatUser {
  name: string;
  id: string;
  username: string;
}

const ChatDrawer: React.FC<ChatDrawerProps> = ({ userId, userRole, targetUserId, onClose }) => {
  // tokens are stored in localStorage under 'access_token'
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [adminTargetId, setAdminTargetId] = useState(targetUserId || '');
  const [userList, setUserList] = useState<ChatUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<ChatUser | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch user list for admin
  useEffect(() => {
    if (userRole === 'admin') {
      fetchUserList();
    }
  }, [userRole]);

  const fetchUserList = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(apiUrl('/api/admin/users/only-users'), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!res.ok) return;
      const data = await res.json();
      setUserList(data.users || []);
      // Auto-select first user if none selected
      if (!selectedUser && data.users && data.users.length > 0) {
        setSelectedUser(data.users[0]);
        setAdminTargetId(data.users[0].id);
      }
    } catch (error) {
      console.error("Failed to fetch UserList: ",error);
    }
  };

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchMessages = useCallback(async () => {
    try {
      const id = userRole === 'admin' ? adminTargetId : userId;
      if (!id) return;
      const token = localStorage.getItem('access_token');
      const res = await fetch(apiUrl(`/api/chat/messages?user_id=${id}`), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!res.ok) return;
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error("Failed to fetch messages: ", error);
    }
  }, [userRole, adminTargetId, userId]);

  // Poll for messages
  useEffect(() => {
    if (!userId || (userRole === 'admin' && !adminTargetId)) return;
    fetchMessages();
    const interval = window.setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, [userId, userRole, adminTargetId, fetchMessages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
      const payload = {
        to_id: userRole === 'admin' ? adminTargetId : 'admin',
        to_role: userRole === 'admin' ? 'user' : 'admin',
        content: input.trim(),
      };
      const token = localStorage.getItem('access_token');
      const res = await fetch(apiUrl('/api/chat/send'), {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setInput('');
        fetchMessages();
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle user selection (admin)
  const handleUserSelect = (user: ChatUser) => {
    setSelectedUser(user);
    setAdminTargetId(user.id);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/40" onClick={onClose}></div>
      {/* Drawer */}
      <div className="relative w-full sm:max-w-2xl bg-white dark:bg-slate-900 h-full shadow-2xl flex flex-col sm:flex-row rounded-none sm:rounded-l-2xl border-l-0 sm:border-l-4 border-yellow-500">
        {/* Responsive: User List for Admin (stacked on top for mobile, left for desktop) */}
        {userRole === 'admin' && (
          <div className="w-full sm:w-64 border-b sm:border-b-0 sm:border-r border-yellow-500 bg-white dark:bg-slate-900 flex flex-col rounded-none sm:rounded-l-2xl">
            <div className="p-3 sm:p-4 font-bold border-b border-yellow-500 text-gray-700 dark:text-gray-200 bg-white dark:bg-slate-900 rounded-none sm:rounded-tl-2xl text-base sm:text-lg">Users</div>
            <div className="flex-1 overflow-y-auto custom-scrollbar max-h-32 sm:max-h-none">
              {userList.length === 0 ? (
                <div className="text-yellow-700 text-center mt-4 sm:mt-8 text-sm sm:text-base">Loading...</div>
              ) : (
                <ul className="flex flex-row sm:flex-col overflow-x-auto sm:overflow-x-visible">
                  {userList.map((user) => (
                    <li
                      key={user.id}
                      className={`cursor-pointer px-3 py-2 sm:px-4 sm:py-3 border-b-0 sm:border-b border-r sm:border-r-0 border-gray-100 dark:border-slate-700 hover:bg-yellow-50 dark:hover:bg-slate-800 transition-colors duration-150 ${selectedUser?.id === user.id ? 'bg-yellow-100 dark:bg-slate-700 font-bold text-yellow-700 dark:text-yellow-400' : 'text-gray-800 dark:text-gray-200'} text-xs sm:text-base whitespace-nowrap`}
                      onClick={() => handleUserSelect(user)}
                    >
                      <div className="truncate">{user.name || user.id}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
        {/* Chat Panel */}
        <div className="flex-1 flex flex-col bg-white rounded-none sm:rounded-r-2xl">
          <div className="flex items-center justify-between p-3 sm:p-4 border-b border-yellow-500 bg-white dark:bg-slate-900 rounded-none sm:rounded-tr-2xl">
            <h2 className="text-base sm:text-lg font-bold text-gray-700 dark:text-gray-200">
              Chat {userRole === 'admin' ? `with ${selectedUser?.name || ''}` : 'with Admin'}
            </h2>
            <button onClick={onClose} className="text-yellow-500 hover:text-yellow-700 dark:hover:text-yellow-400 text-2xl sm:text-2xl font-bold px-2 py-1 sm:px-0 sm:py-0">&times;</button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-2 sm:space-y-3 custom-scrollbar bg-white dark:bg-slate-900">
            {messages.length === 0 ? (
              <div className="text-gray-400 dark:text-gray-500 text-center text-sm sm:text-base">No messages yet.</div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={msg._id || idx}
                  className={`max-w-[90%] sm:max-w-[70%] px-3 sm:px-4 py-2 rounded-2xl text-sm sm:text-base shadow mb-1 sm:mb-2
                    ${msg.from_id === userId
                      ? 'bg-yellow-100 dark:bg-yellow-500/20 text-gray-900 dark:text-yellow-100 ml-auto rounded-br-none border border-yellow-200 dark:border-yellow-500/40'
                      : 'bg-gray-100 dark:bg-slate-800 text-gray-900 dark:text-gray-200 mr-auto rounded-bl-none border border-gray-200 dark:border-slate-700'}`}
                >
                  {msg.content}
                  <div className="text-xs text-right mt-1 opacity-60 dark:text-gray-400">
                    {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="p-3 sm:p-4 border-t border-yellow-500 bg-white dark:bg-gray-900 flex gap-1 sm:gap-2 rounded-none sm:rounded-b-2xl">
            <input
              type="text"
              className="flex-1 px-3 sm:px-4 py-2 rounded-full border border-yellow-500 bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-yellow-400 placeholder-gray-400 dark:placeholder-gray-500 text-sm sm:text-base"
              placeholder="Type a message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') sendMessage(); }}
              disabled={loading || (userRole === 'admin' && !adminTargetId)}
            />
            <button
              onClick={sendMessage}
              className="bg-yellow-400 hover:bg-yellow-500 text-black dark:text-slate-900 px-4 sm:px-6 py-2 rounded-full font-bold shadow-md transition disabled:opacity-50 text-sm sm:text-base"
              disabled={loading || !input.trim() || (userRole === 'admin' && !adminTargetId)}
            >
              Send
            </button>
          </div>
        </div>
      </div>
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #fde047;
          border-radius: 4px;
        }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #facc15;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #fffbea;
        }
        .dark .custom-scrollbar::-webkit-scrollbar-track {
          background: #020617;
        }
      `}</style>
    </div>
  );
};

export default ChatDrawer; 
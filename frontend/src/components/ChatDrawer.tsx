import React, { useState, useEffect, useRef } from 'react';
import { useClerk } from '@clerk/clerk-react';

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
  const clerk = useClerk();
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [pollInterval, setPollInterval] = useState<number | null>(null);
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
      const token = await clerk.session?.getToken();
      const res = await fetch('http://127.0.0.1:5000/api/admin/users/only-users', {
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
    } catch {}
  };

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Poll for messages
  useEffect(() => {
    const id = userRole === 'admin' ? adminTargetId : userId;
    if (!userId || (userRole === 'admin' && !adminTargetId)) return;
    fetchMessages();
    if (pollInterval) clearInterval(pollInterval);
    const interval = window.setInterval(fetchMessages, 5000);
    setPollInterval(interval);
    return () => clearInterval(interval);
    // eslint-disable-next-line
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
    } catch {}
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
      const payload = {
        to_id: userRole === 'admin' ? adminTargetId : 'admin',
        to_role: userRole === 'admin' ? 'user' : 'admin',
        content: input.trim(),
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
      <div className="fixed inset-0 bg-black bg-opacity-40" onClick={onClose}></div>
      {/* Drawer */}
      <div className="relative w-full sm:max-w-2xl bg-white h-full shadow-2xl flex flex-col sm:flex-row rounded-none sm:rounded-l-2xl border-l-0 sm:border-l-4 border-yellow-500">
        {/* Responsive: User List for Admin (stacked on top for mobile, left for desktop) */}
        {userRole === 'admin' && (
          <div className="w-full sm:w-64 border-b sm:border-b-0 sm:border-r border-yellow-500 bg-white flex flex-col rounded-none sm:rounded-l-2xl">
            <div className="p-3 sm:p-4 font-bold border-b border-yellow-500 text-gray-700 bg-white rounded-none sm:rounded-tl-2xl text-base sm:text-lg">Users</div>
            <div className="flex-1 overflow-y-auto custom-scrollbar max-h-32 sm:max-h-none">
              {userList.length === 0 ? (
                <div className="text-yellow-700 text-center mt-4 sm:mt-8 text-sm sm:text-base">Loading...</div>
              ) : (
                <ul className="flex flex-row sm:flex-col overflow-x-auto sm:overflow-x-visible">
                  {userList.map((user) => (
                    <li
                      key={user.id}
                      className={`cursor-pointer px-3 py-2 sm:px-4 sm:py-3 border-b-0 sm:border-b border-r sm:border-r-0 border-gray-100 hover:bg-yellow-50 transition-colors duration-150 ${selectedUser?.id === user.id ? 'bg-yellow-100 font-bold text-yellow-700' : 'text-gray-800'} text-xs sm:text-base whitespace-nowrap`}
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
          <div className="flex items-center justify-between p-3 sm:p-4 border-b border-yellow-500 bg-white rounded-none sm:rounded-tr-2xl">
            <h2 className="text-base sm:text-lg font-bold text-gray-700">
              Chat {userRole === 'admin' ? `with ${selectedUser?.name || ''}` : 'with Admin'}
            </h2>
            <button onClick={onClose} className="text-yellow-500 hover:text-yellow-700 text-2xl sm:text-2xl font-bold px-2 py-1 sm:px-0 sm:py-0">&times;</button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-2 sm:space-y-3 custom-scrollbar bg-white">
            {messages.length === 0 ? (
              <div className="text-gray-400 text-center text-sm sm:text-base">No messages yet.</div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={msg._id || idx}
                  className={`max-w-[90%] sm:max-w-[70%] px-3 sm:px-4 py-2 rounded-2xl text-sm sm:text-base shadow mb-1 sm:mb-2
                    ${msg.from_id === userId
                      ? 'bg-yellow-100 text-gray-900 ml-auto rounded-br-none border border-yellow-200'
                      : 'bg-gray-100 text-gray-900 mr-auto rounded-bl-none border border-gray-200'}`}
                >
                  {msg.content}
                  <div className="text-xs text-right mt-1 opacity-60">
                    {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className="p-3 sm:p-4 border-t border-yellow-500 bg-white flex gap-1 sm:gap-2 rounded-none sm:rounded-b-2xl">
            <input
              type="text"
              className="flex-1 px-3 sm:px-4 py-2 rounded-full border border-yellow-500 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-yellow-400 placeholder-gray-400 text-sm sm:text-base"
              placeholder="Type a message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') sendMessage(); }}
              disabled={loading || (userRole === 'admin' && !adminTargetId)}
            />
            <button
              onClick={sendMessage}
              className="bg-yellow-400 hover:bg-yellow-500 text-black px-4 sm:px-6 py-2 rounded-full font-bold shadow-md transition disabled:opacity-50 text-sm sm:text-base"
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
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #fffbea;
        }
      `}</style>
    </div>
  );
};

export default ChatDrawer; 
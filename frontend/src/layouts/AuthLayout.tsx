import { Outlet, Link } from 'react-router-dom';
import { SignedIn, RedirectToSignIn } from '@clerk/clerk-react';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../context/ThemeContext';
import { motion } from 'framer-motion';

const FloatingParticles = () => (
  <div className="absolute inset-0 overflow-hidden">
    {[...Array(30)].map((_, i) => (
      <motion.div
        key={i}
        className="absolute w-2 h-2 bg-yellow-400 rounded-full"
        initial={{
          x: Math.random() * window.innerWidth,
          y: Math.random() * window.innerHeight,
        }}
        animate={{
          y: [
            Math.random() * window.innerHeight,
            Math.random() * window.innerHeight,
          ],
          x: [
            Math.random() * window.innerWidth,
            Math.random() * window.innerWidth,
          ],
        }}
        transition={{
          duration: Math.random() * 50 + 20,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    ))}
  </div>
);

const GradientBackground = () => (
  <div className="absolute inset-0">
    <div className="absolute inset-0 bg-gradient-to-br from-yellow-100/30 via-white to-yellow-50/30 dark:from-white dark:via-yellow-200 dark:to-white" />
    <motion.div
      animate={{
        scale: [1, 1.2, 1],
        opacity: [0.3, 0.2, 0.3],
      }}
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: "easeInOut"
      }}
      className="absolute top-0 left-0 w-full h-full bg-gradient-to-br
       from-yellow-200/20 to-transparent dark:from-yellow-900/10"
      style={{ filter: 'blur(100px)' }}
    />
  </div>
);

const AuthLayout = () => {
  // const { theme, toggleTheme } = useTheme();

  return (
    <div className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-hidden bg-yellow-200">
      {/* Background Effects */}
      <GradientBackground />
      {/* <FloatingParticles /> */}
      
      <SignedIn>
        <RedirectToSignIn />
      </SignedIn>


      {/* Main Container */}
      <div className="relative w-full max-w-md px-4 z-10 mt-10">
        {/* Logo Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          {/* <Link to="/" className="inline-block group"> */}
            <div className="flex items-center justify-center gap-3 mb-2">
              <motion.img 
                src="/favicon.png" 
                alt="Beehive Logo" 
                className="w-12 h-12"
                whileHover={{ scale: 1.1, rotate: 10 }}
                transition={{ type: "spring", stiffness: 400 }}
              />
              <h1 className="text-3xl font-bold bg-clip-text text-black bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400">
                Beehive
              </h1>
            </div>
            <p className="text-gray-700 dark:text-gray-400 text-sm">
              Transforming Alaska's Behavioral Health
            </p>
          {/* </Link> */}
        </motion.div>

        {/* Auth Card Container */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="relative mb-20">
            {/* Card Glow Effect */}
            <div 
              className="absolute -inset-1 rounded-2xl blur-3xl"
            />
            
            {/* Main Card */}
            {/* <div className="relative bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl shadow-2xl rounded-2xl border border-gray-200/50 dark:border-gray-700/50"> */}
              <div className="p-2">
                <Outlet />
              {/* </div> */}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="fixed bottom-6 text-center text-sm mt-10"
      >
        <p className="text-gray-600 dark:text-gray-500">
          © {new Date().getFullYear()} Beehive. All rights reserved.
        </p>
      </motion.div>
    </div>
  );
};

export default AuthLayout; 
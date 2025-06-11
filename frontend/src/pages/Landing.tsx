import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SignedIn, SignedOut, useUser } from '@clerk/clerk-react';
import { useAuth } from '../hooks/useAuth';
import Spotlightcard from '../components/ui/Spotlightcard';
import Blurtext from '../components/ui/Blurtext';
import CardSwap,{Card} from '../components/ui/CardSwap';

interface MousePosition {
  x: number;
  y: number;
}

interface SpotlightEffectProps {
  mousePosition: MousePosition;
}

const HoneycombBackground = () => {
  return (
    <div className="absolute inset-0 -z-10 overflow-hidden opacity-20">
      {[...Array(30)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute bg-yellow-400/10 backdrop-blur-sm"
          style={{
            width: '200px',
            height: '200px',
            clipPath: 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)',
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 60, 0],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 10 + Math.random() * 10,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      ))}
    </div>
  );
};

const SpotlightEffect = ({ mousePosition }: SpotlightEffectProps) => {
  return (
    <div 
      className="pointer-events-none absolute inset-0 -z-5 opacity-70 mix-blend-soft-light"
      style={{
        background: `
          radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, 
          rgba(250, 204, 21, 0.15),
          transparent 40%
          )
        `
      }}
    />
  );
};

const Landing = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isScrolled, setIsScrolled] = useState(false);
  const navigate = useNavigate();
  const { isAdmin, isUser } = useAuth();
  const { user } = useUser();
  const { scrollY } = useScroll();

  useEffect(() => {
    setIsLoaded(true);
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const handleGetStarted = () => {
    if (user) {
      if (isAdmin()) {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } else {
      navigate('/sign-up');
    }
  };

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      <HoneycombBackground />
      <SpotlightEffect mousePosition={mousePosition} />

      {/* Navigation */}
      <motion.nav
        className={`fixed w-full z-50 transition-all duration-300 ${
          isScrolled
            ? 'mt-8 ml-6 lg:ml-12 mx-auto max-w-[90%] rounded-full bg-gray-50/90 backdrop-blur-md shadow-lg'
            : 'bg-gray-100/80 backdrop-blur-md shadow-sm'
        }`}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className={`max-w-7xl mx-auto px-4 lg:px-8 transition-all duration-300 ${
          isScrolled ? 'py-4' : 'py-4'
        }`}>
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center space-x-3"
            >
              <motion.img 
                src="/favicon.png" 
                alt="Beehive Logo" 
                className={`transition-all duration-300 ${
                  isScrolled ? 'h-8 w-8' : 'h-10 w-10'
                }`}
                whileHover={{ scale: 1.1, rotate: 10 }}
                transition={{ type: "spring", stiffness: 300 }}
              />
              <span className={`font-bold text-black transition-all duration-300 ${
                isScrolled ? 'text-xl' : 'text-2xl'
              }`}>
                Beehive
              </span>
            </motion.div>
            
            <div className="flex items-center space-x-8">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="hidden md:flex space-x-8"
              >
                {["About", "Features", "Contact"].map((item, index) => (
                  <motion.a
                    key={item}
                    href={`#${item.toLowerCase()}`}
                    className={`text-gray-800 hover:text-yellow-500 transition-all duration-300 ${
                      isScrolled ? 'text-sm' : 'text-base'
                    } relative group`}
                    whileHover={{ scale: 1.05 }}
                  >
                    {item}
                    <motion.span
                      className="absolute bottom-0 left-0 w-0 h-0.5 bg-yellow-400 group-hover:w-full transition-all duration-300"
                      initial={{ width: "0%" }}
                      whileHover={{ width: "100%" }}
                    />
                  </motion.a>
                ))}
              </motion.div>

              {/* Auth Buttons */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="flex items-center space-x-4"
              >
                <SignedIn>
                  <motion.button
                    onClick={() => {
                      if (isAdmin()) {
                        navigate('/admin');
                      } else {
                        navigate('/dashboard');
                      }
                    }}
                    className={`bg-yellow-400 text-black rounded-full hover:bg-yellow-500 transition-all shadow-md hover:shadow-lg ${
                      isScrolled ? 'px-4 py-1.5 text-sm' : 'px-6 py-2 text-base'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Dashboard
                  </motion.button>
                </SignedIn>
                <SignedOut>
                  <motion.button
                    onClick={() => navigate('/sign-in')}
                    className={`text-gray-800 hover:text-yellow-500 transition-colors ${
                      isScrolled ? 'text-sm' : 'text-base'
                    }`}
                    whileHover={{ scale: 1.05 }}
                  >
                    Sign In
                  </motion.button>
                  <motion.button
                    onClick={() => navigate('/sign-up')}
                    className={`bg-yellow-400 text-black rounded-full hover:bg-yellow-500 transition-all shadow-md hover:shadow-lg ${
                      isScrolled ? 'px-4 py-1.5 text-sm' : 'px-6 py-2 text-base'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Sign Up
                  </motion.button>
                </SignedOut>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative mt-20">
        <div className="max-w-7xl mx-auto ">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Blurtext
              text="Transforming Alaska's Behavioral Health Insights"
              className="text-5xl md:text-6xl font-bold text-black mb-6 [&>span:nth-child(2)]:text-yellow-500"
              delay={200}
              animateBy="words"
              direction="top"
            />
            <motion.p 
              className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              A data-driven initiative enhancing behavioral health insights and healthcare practices 
              in Alaska through a federated data approach.
            </motion.p>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="space-x-4"
            >
              <SignedOut>
                <motion.button
                  onClick={handleGetStarted}
                  className="bg-yellow-400 text-black px-8 py-3 rounded-full hover:bg-yellow-500 transition-all shadow-lg hover:shadow-xl"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Get Started
                </motion.button>
                <motion.button
                  onClick={() => navigate('/sign-in')}
                  className="bg-black text-white px-8 py-3 rounded-full border-2 border-black hover:bg-gray-900 transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Sign In
                </motion.button>
              </SignedOut>
              <SignedIn>
                <motion.button
                  onClick={handleGetStarted}
                  className="bg-yellow-400 text-black px-8 py-3 rounded-full hover:bg-yellow-500 transition-all shadow-lg hover:shadow-xl"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Go to Dashboard
                </motion.button>
              </SignedIn>
            </motion.div>
          </motion.div>

          {/* Card Section */}
          <section id="cards" className="relative overflow-hidden">
            <div className="lg:py-32 py-10">
              <div className="max-w-[1400px] mx-auto px-4 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                {/* Quote Section */}
                <motion.div 
                  initial={{ opacity: 0, x: -50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.8 }}
                  className="relative z-10"
                >
                  <div className="relative">
                    <motion.div
                      initial={{ scale: 0.9, opacity: 0 }}
                      whileInView={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 0.2, duration: 0.5 }}
                      className="absolute -top-8 -left-8 text-8xl text-yellow-400 opacity-30"
                    >
                      "
                    </motion.div>
                    <motion.blockquote
                      initial={{ y: 20, opacity: 0 }}
                      whileInView={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.3, duration: 0.8 }}
                      className="text-3xl font-light text-gray-800 leading-relaxed mb-8"
                    >
                      Transforming healthcare data into actionable insights, one decision at a time.
                    </motion.blockquote>
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      whileInView={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.5, duration: 0.8 }}
                      className="flex items-center space-x-4"
                    >
                      <div className="w-12 h-1 bg-yellow-400"></div>
                      <p className="text-gray-600 font-medium">Beehive Developer Community</p>
                    </motion.div>
                  </div>

                  {/* Stats */}
                  <motion.div 
                    initial={{ y: 30, opacity: 0 }}
                    whileInView={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.7, duration: 0.8 }}
                    className="grid grid-cols-2 gap-8 mt-12"
                  >
                    <div className="p-6 bg-gray-100 rounded-xl shadow-xl hover:shadow-2xl transition-shadow duration-300">
                      <div className="text-3xl font-bold text-yellow-500 mb-2">99.9%</div>
                      <div className="text-gray-600">Uptime Reliability</div>
                    </div>
                    <div className="p-6 bg-gray-100 rounded-xl shadow-xl hover:shadow-2xl transition-shadow duration-300">
                      <div className="text-3xl font-bold text-yellow-500 mb-2">24/7</div>
                      <div className="text-gray-600">Support Available</div>
                    </div>
                  </motion.div>
                </motion.div>

                {/* Cards */}
                
                <div className="hidden lg:block" style={{ height: '600px', position: 'relative' }}>
                  <CardSwap
                    cardDistance={60}
                    verticalDistance={70}
                    delay={3000}
                    pauseOnHover={true}
                    skewAmount={2}
                    width={550}
                    height={450}
                  >
                    <Card className="p-8 bg-gradient-to-br from-gray-900 to-black">
                      <div className="relative h-64 mb-6 overflow-hidden rounded-xl">
                        <img 
                          src="/card1.png" 
                          alt="Admin Dashboard" 
                          className="w-full h-full object-cover transform hover:scale-105 transition-transform duration-300" 
                        />
                        <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                          <span className="text-white text-sm font-medium px-3 py-1 bg-yellow-500/80 rounded-full">
                            Admin Dashboard
                          </span>
                        </div>
                      </div>
                      <h3 className='text-white text-2xl font-bold mb-3'>Powerful Admin Controls</h3>
                      <p className='text-gray-300 leading-relaxed'>
                        Comprehensive admin dashboard with real-time analytics, user management, and data visualization tools.
                        Monitor system performance and manage permissions with ease.
                      </p>
                    </Card>

                    <Card className="p-8 bg-gradient-to-br from-gray-900 to-black">
                      <div className="relative h-64 mb-6 overflow-hidden rounded-xl">
                        <img 
                          src="/card3.png" 
                          alt="User Dashboard" 
                          className="w-full h-full object-cover transform hover:scale-105 transition-transform duration-300" 
                        />
                        <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                          <span className="text-white text-sm font-medium px-3 py-1 bg-yellow-500/80 rounded-full">
                            User Dashboard
                          </span>
                        </div>
                      </div>
                      <h3 className='text-white text-2xl font-bold mb-3'>Intuitive User Interface</h3>
                      <p className='text-gray-300 leading-relaxed'>
                        Clean and user-friendly dashboard for healthcare providers. Access patient data,
                        generate reports, and collaborate seamlessly.
                      </p>
                    </Card>

                    <Card className="p-8 bg-gradient-to-br from-gray-900 to-black">
                      <div className="relative h-64 mb-6 overflow-hidden rounded-xl">
                        <img 
                          src="/card2.png" 
                          alt="Data Analytics" 
                          className="w-full h-full object-cover transform hover:scale-105 transition-transform duration-300" 
                        />
                        <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                          <span className="text-white text-sm font-medium px-3 py-1 bg-yellow-500/80 rounded-full">
                            Data Analytics
                          </span>
                        </div>
                      </div>
                      <h3 className='text-white text-2xl font-bold mb-3'>Advanced Analytics</h3>
                      <p className='text-gray-300 leading-relaxed'>
                        Powerful data visualization and analysis tools. Transform complex healthcare data
                        into actionable insights with interactive charts and reports.
                      </p>
                    </Card>
                  </CardSwap>
                </div>
              </div>
            </div>

            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 0.05 }}
                transition={{ duration: 1 }}
                className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-yellow-400 rounded-full blur-[100px]"
              />
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 0.05 }}
                transition={{ duration: 1, delay: 0.3 }}
                className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-yellow-400 rounded-full blur-[100px]"
              />
            </div>
          </section>

          {/* Features Section */}
          <div className="max-w-7xl mx-auto mt-10 ">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <Blurtext
              text="Powerful Features for Better Healthcare"
              className="text-4xl md:text-5xl font-bold text-black mb-6"
              delay={100}
              animateBy="words"
            />
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover how Beehive is revolutionizing behavioral health data management in Alaska
            </p>
          </motion.div>
          </div>
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20"
          >
            {[
              {
                title: "Data Federation",
                description: "Secure and efficient sharing of behavioral health data across Alaska",
                icon: "📊"
              },
              {
                title: "Healthcare Insights",
                description: "Advanced analytics for better healthcare decision making",
                icon: "🏥"
              },
              {
                title: "Community Impact",
                description: "Improving behavioral health outcomes for Alaskans",
                icon: "🤝"
              }
            ].map((feature, index) => (
              <Spotlightcard
                key={index}
                className="p-8"
                spotlightColor="rgba(255, 204, 0, 0.54)"
              >
                <motion.div 
                  className="text-4xl mb-4"
                  whileHover={{ scale: 1.2, rotate: 10 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  {feature.icon}
                </motion.div>
                <h3 className="text-white text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </Spotlightcard>
            ))}
          </motion.div>
        </div>
      </section>

      

      {/* About Section */}
      <section id="about" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <Blurtext
                text="Our Mission"
                className="text-4xl md:text-5xl font-bold text-black mb-6"
                delay={100}
                animateBy="words"
              />
              <div className="space-y-6 text-gray-600">
                <p className="text-lg">
                  At Beehive, we're committed to transforming behavioral healthcare in Alaska through innovative data solutions and collaborative approaches.
                </p>
                <p className="text-lg">
                  Our platform enables healthcare providers to make data-driven decisions while ensuring the highest standards of privacy and security.
                </p>
                <motion.button
                  className="bg-yellow-400 text-black px-8 py-3 rounded-full hover:bg-yellow-500 transition-all shadow-lg hover:shadow-xl mt-4"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/about')}
                >
                  Learn More
                </motion.button>
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="aspect-w-16 aspect-h-9 rounded-xl overflow-hidden shadow-2xl">
                <img
                  src="/healthcare.jpeg"
                  alt="Healthcare professionals collaborating"
                  className="object-cover"
                />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <Blurtext
              text="Get in Touch"
              className="text-4xl md:text-5xl font-bold text-black mb-6"
              delay={100}
              animateBy="words"
            />
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Have questions about Beehive? We're here to help!
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="bg-white p-8 rounded-xl shadow-lg"
            >
              <form className="space-y-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    className="mt-1 block w-full rounded-md border border-gray-300 bg-white shadow-sm focus:border border-yellow-500 focus:ring-yellow-500"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    className="mt-1 block w-full rounded-md border border-gray-300 bg-white shadow-sm focus:border border-yellow-500 focus:ring-yellow-500"
                  />
                </div>
                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700">
                    Message
                  </label>
                  <textarea
                    id="message"
                    rows={4}
                    className="mt-1 block w-full rounded-md border border-gray-300 bg-white shadow-sm focus:border border-yellow-500 focus:ring-yellow-500"
                  ></textarea>
                </div>
                <motion.button
                  type="submit"
                  className="w-full bg-yellow-400 text-black px-8 py-3 rounded-full hover:bg-yellow-500 transition-all shadow-lg hover:shadow-xl"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Send Message
                </motion.button>
              </form>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-8"
            >
              {[
                {
                  title: "Office Location",
                  description: "123 Healthcare Avenue, Anchorage, Alaska 99501",
                  icon: "📍"
                },
                {
                  title: "Email Us",
                  description: "contact@beehive-health.com",
                  icon: "✉️"
                },
                {
                  title: "Call Us",
                  description: "(907) 555-0123",
                  icon: "📞"
                },
                {
                  title: "Business Hours",
                  description: "Monday - Friday: 9:00 AM - 5:00 PM AKST",
                  icon: "🕒"
                }
              ].map((item, index) => (
                <motion.div
                  key={index}
                  className="flex items-start space-x-4"
                  whileHover={{ x: 5 }}
                >
                  <div className="text-3xl">{item.icon}</div>
                  <div>
                    <h3 className="text-lg font-semibold">{item.title}</h3>
                    <p className="text-gray-600">{item.description}</p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>
      
      

      {/* Footer */}
      <footer className="bg-black text-white py-12 px-4 relative overflow-hidden">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 relative z-10">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            <div className="flex items-center space-x-2">
              <img src="/favicon.png" alt="Beehive Logo" className="h-8 w-8" />
              <span className="text-xl font-bold text-yellow-400">Beehive</span>
            </div>
            <p className="text-gray-400">Transforming behavioral healthcare through data-driven insights.</p>
          </motion.div>

          {[
            {
              title: "Company",
              links: [
                { name: "About Us", href: "/about" },
                { name: "Privacy Policy", href: "/privacy" },
                { name: "Terms of Service", href: "/terms" },
                { name: "Contact", href: "#contact" }
              ]
            },
            {
              title: "Resources",
              links: [
                { name: "Documentation", href: "#" },
                { name: "API", href: "#" },
                { name: "Support", href: "#" },
                { name: "Blog", href: "#" }
              ]
            },
            {
              title: "Connect",
              links: [
                { name: "Twitter", href: "#" },
                { name: "LinkedIn", href: "#" },
                { name: "Facebook", href: "#" },
                { name: "GitHub", href: "#" }
              ]
            }
          ].map((section, index) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="space-y-4"
            >
              <h4 className="text-lg font-semibold text-yellow-400">{section.title}</h4>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.name}>
                    <motion.a
                      href={link.href}
                      className="text-gray-400 hover:text-yellow-400 transition-colors"
                      whileHover={{ x: 5 }}
                    >
                      {link.name}
                    </motion.a>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-12 pt-8 border-t border-gray-800 text-center text-gray-400"
        >
          <p>© {new Date().getFullYear()} Beehive. All rights reserved.</p>
        </motion.div>

        {/* Footer Honeycomb Background */}
        <div className="absolute inset-0 opacity-5">
          {[...Array(15)].map((_, i) => (
            <div
              key={i}
              className="absolute bg-yellow-400"
              style={{
                width: '100px',
                height: '100px',
                clipPath: 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)',
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                transform: `rotate(${Math.random() * 360}deg)`,
              }}
            />
          ))}
        </div>
      </footer>
    </div>
  );
};

export default Landing; 
import { motion } from 'framer-motion';
import Blurtext from '../components/ui/Blurtext';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../context/ThemeContext';

interface TeamMember {
  name: string;
  role: string;
  affiliation: string;
  image: string;
  bio?: string;
}

const AboutUs = () => {
  const { theme, toggleTheme } = useTheme();
  const teamMembers: TeamMember[] = [
    {
      name: "Pradeeban Kathiravelu",
      role: "Org Maintainer - Project Lead",
      affiliation: "University of Alaska Anchorage",
      image: "/team/member1.jpeg",
      bio: "Leading the development of Beehive and mentoring the team."
    },
    {
      name: "David Moxley",  
      role: "Org Maintainer - Project Lead",
      affiliation: "University of Alaska Anchorage",
      image: "/team/member6.jpeg",
      bio: "Guiding the project's vision and research direction."
    },
    {
      name: "Ishaan Gupta",
      role: "Developer",
      affiliation: "Google Summer of Code - 25",
      image: "/team/member2.jpeg",
      bio: "Contributing to the frontend development and user experience."
    },
    {
      name: "Bagwan Prasad",
      role: "Developer",
      affiliation: "Google Summer of Code - 25",
      image: "/team/member3.jpeg",
      bio: "Working on backend infrastructure and data management."
    },
    {
      name: "Mohamed Abdullah",
      role: "Developer",
      affiliation: "Alaskan Season of Code - 24",
      image: "/team/member4.png",
      bio: "Focusing on system architecture and integration."
    },
 
    // Add more team members as needed
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-300">
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-yellow-300 dark:bg-yellow-600 transition-colors duration-300">
        {/* Dark Mode Toggle - Top Right Corner */}
        <motion.button
          onClick={toggleTheme}
          className="fixed top-6 right-6 z-50 p-3 rounded-lg transition-all duration-200 shadow-lg bg-white hover:bg-gray-100 text-gray-800 border border-gray-200 dark:border-none dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-yellow-400 dark:shadow-yellow-400/20"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? (
            <SunIcon className="h-5 w-5" />
          ) : (
            <MoonIcon className="h-5 w-5" />
          )}
        </motion.button>
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Blurtext
              text="About Beehive Project"
              className="text-5xl md:text-6xl font-bold text-black mb-6 dark:text-white"
              delay={100}
              animateBy="words"
            />
            <p className="text-xl text-gray-600 dark:text-gray-200 max-w-3xl mx-auto">
              A collaboration between UAA Departments of Computer Science and Human Services
            </p>
          </motion.div>
        </div>
      </section>

      {/* Project Overview */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-800 transition-colors duration-300">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="prose prose-lg max-w-none dark:prose-invert"
          >
            <h2 className="text-3xl font-bold mb-8 text-yellow-600 dark:text-yellow-400">The 49th State Initiative</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Anchorage, the largest city in Alaska, has a vibrant open-source community. Through this GSoC initiative, industrial experts that are part of Alaska Developer Alliance and faculty and researchers from the University of Alaska Anchorage (UAA) and University of Alaska Fairbanks (UAF) join hands, to provide a perfect mentoring experience for interested contributors globally.
            </p>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              We provide a glimpse of this northern state and its tech landscape to the Lower 48 and the outside world through this open-source remote summer coding program organized and funded by Google. Our projects focus on healthcare, climate science, polar science, and other research fields critical to the Circumpolar North and the rest of the world.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Project Goals */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-100 dark:bg-gray-700 transition-colors duration-300">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl font-bold mb-8 text-yellow-600 dark:text-yellow-400">Project Goals</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg dark:shadow-gray-900/50">
                <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Digital Repository Creation</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Create a digital repository of images, particularly focusing on Outsider Art, produced by individuals who aren't formally trained as artists and experience considerable discrimination. This repository will support research, education, and arts programs.
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg dark:shadow-gray-900/50">
                <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Healthcare Advancement</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Support research on Outsider art and Artists, educate health and human services practitioners about the impact of negative stereotypes, and advance arts programs devoted to improving the health of vulnerable people.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Project Details */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-800 transition-colors duration-300">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="prose prose-lg max-w-none dark:prose-invert"
          >
            <h2 className="text-3xl font-bold mb-8 text-yellow-600 dark:text-yellow-400">Project Description</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              This project, a collaboration between the University of Alaska Anchorage Departments of Computer Science and Human Services, seeks to create a digital approach to translating the digitalization of art and photographic images into a digital database that stores in retrievable formats those images for use in advancing the delivery of human services and health care to people who experience considerable vulnerability and marginalization within the community.
            </p>
            <p className="text-gray-600 dark:text-gray-300">
              The project aims to develop <span className='text-yellow-500 dark:text-yellow-400'>Beehive </span> as a prototype implementation of an open-source data federation framework that can be used in research environments in Alaska and elsewhere.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-100 dark:bg-gray-700 transition-colors duration-300">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">Our Team</h2>
            <div className="w-24 h-1 bg-yellow-400 mx-auto mb-8"></div>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Meet the brilliant minds behind Beehive - a diverse team of researchers, developers, and innovators working together to transform healthcare data management.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
            {teamMembers.map((member, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="group relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg dark:shadow-gray-900/50 hover:shadow-2xl dark:hover:shadow-gray-900/70 transition-all duration-300 overflow-hidden"
              >
                {/* Hexagon Background Pattern */}
                {/* <div className="absolute inset-0 opacity-0 group-hover:opacity-30 transition-opacity duration-300">
                  {[...Array(6)].map((_, i) => (
                    <div
                      key={i}
                      className="absolute bg-yellow-500"
                      style={{
                        width: '60px',
                        height: '60px',
                        clipPath: 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)',
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                        transform: `rotate(${Math.random() * 360}deg)`,
                      }}
                    />
                  ))}
                </div> */}

                <div className="p-6">
                  <div className="relative">
                    <div className="w-32 h-32 mx-auto mb-6 rounded-full overflow-hidden ring-4 ring-yellow-400/30 group-hover:ring-yellow-400 transition-all duration-300">
                      <img
                        src={member.image}
                        alt={member.name}
                        className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-300"
                      />
                    </div>
                  </div>

                  <div className="text-center">
                    <h3 className="text-xl font-bold mb-1 text-gray-900 dark:text-white group-hover:text-yellow-500 transition-colors">
                      {member.name}
                    </h3>
                    <p className="text-yellow-500 dark:text-yellow-400 font-medium mb-2">{member.role}</p>
                    <p className="text-gray-600 dark:text-gray-300 mb-3">{member.affiliation}</p>
                    <p className="text-gray-500 dark:text-gray-400 text-sm italic opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      {member.bio}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutUs; 

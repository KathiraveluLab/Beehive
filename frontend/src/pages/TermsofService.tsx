import React, { useEffect } from 'react';
import { motion } from 'framer-motion';

const TermsOfService: React.FC = () => {
    useEffect(() => {
        window.scrollTo(0, 0);
        document.title = "Terms of Service | Beehive";
    }, []);

    return (
        <div className="min-h-screen bg-gray-100 text-gray-700">
            <main className="pt-24 pb-16">
                <div className="container mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="max-w-3xl mx-auto"
                    >
                        <h1 className="text-3xl md:text-4xl font-bold mb-8 text-yellow-500">Terms of Service</h1>

                        <div className="prose prose-yellow max-w-none">
                            <p className="text-gray-600 mb-4">Last updated: April 14, 2024</p>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Introduction</h2>
                                <p className="text-gray-700">
                                    Welcome to Beehive, a behavioral health analytics platform. These Terms of Service ("Terms") govern your use of our platform and services. By accessing or using Beehive, you agree to be bound by these Terms and our Privacy Policy.
                                </p>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Healthcare Data Compliance</h2>
                                <p className="text-gray-700">
                                    As a platform handling sensitive healthcare information, we maintain strict compliance with:
                                </p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>HIPAA regulations and privacy rules</li>
                                    <li>State and federal healthcare data protection laws</li>
                                    <li>Industry standard security protocols</li>
                                    <li>Data breach notification requirements</li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">User Responsibilities</h2>
                                <p className="text-gray-700">As a user of the Beehive platform, you agree to:</p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>Maintain the confidentiality of your login credentials</li>
                                    <li>Report any unauthorized access immediately</li>
                                    <li>Use the platform in compliance with all applicable healthcare laws</li>
                                    <li>Ensure proper handling of sensitive patient information</li>
                                    <li>Complete required training for platform usage</li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Data Usage and Rights</h2>
                                <p className="text-gray-700">
                                    While using our platform:
                                </p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>You retain ownership of your organization's data</li>
                                    <li>We process data solely for authorized healthcare analytics purposes</li>
                                    <li>Aggregated, de-identified data may be used for research</li>
                                    <li>Data sharing follows strict HIPAA guidelines</li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Prohibited Activities</h2>
                                <p className="text-gray-700">Users must not:</p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>Share access credentials with unauthorized users</li>
                                    <li>Attempt to bypass security measures</li>
                                    <li>Use the platform for non-healthcare purposes</li>
                                    <li>Export data in violation of privacy laws</li>
                                    <li>Introduce malicious software or code</li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Service Availability</h2>
                                <p className="text-gray-700">
                                    We strive to maintain 99.9% uptime, but may occasionally need to perform maintenance or updates. We will provide advance notice of any planned downtime through our notification system.
                                </p>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Termination</h2>
                                <p className="text-gray-700">
                                    We may suspend or terminate access for violations of these Terms or security concerns. Upon termination:
                                </p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>You will receive a copy of your organization's data</li>
                                    <li>Access to the platform will be revoked</li>
                                    <li>Confidentiality obligations remain in effect</li>
                                </ul>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Contact Us</h2>
                                <p className="text-gray-700">
                                    For questions about these Terms, contact our Legal Department:
                                    <br />
                                    <strong>Email:</strong> <a href="mailto:legal@beehive-health.com" className="text-yellow-600 hover:underline">legal@beehive-health.com</a>
                                </p>
                            </section>
                        </div>
                    </motion.div>
                </div>
            </main>
        </div>
    );
};

export default TermsOfService;
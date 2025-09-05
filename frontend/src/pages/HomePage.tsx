import React from 'react';
import { motion } from 'framer-motion';
import HeroSection from '../components/home/HeroSection';
import StatisticsSection from '../components/home/StatisticsSection';
import FeaturedListings from '../components/home/FeaturedListings';
import HowItWorks from '../components/home/HowItWorks';
import CategoriesSection from '../components/home/CategoriesSection';
import TestimonialsSection from '../components/home/TestimonialsSection';
import CTASection from '../components/home/CTASection';

const HomePage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen"
    >
      {/* Hero Section */}
      <HeroSection />
      
      {/* Statistics Section */}
      <StatisticsSection />
      
      {/* Featured Listings */}
      <FeaturedListings />
      
      {/* How It Works */}
      <HowItWorks />
      
      {/* Categories Section */}
      <CategoriesSection />
      
      {/* Testimonials Section */}
      <TestimonialsSection />
      
      {/* Call to Action Section */}
      <CTASection />
    </motion.div>
  );
};

export default HomePage;

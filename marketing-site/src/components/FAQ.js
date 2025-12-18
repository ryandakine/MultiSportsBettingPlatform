import React, { useState } from 'react';
import './FAQ.css';

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: "Why can't I just tail your free picks?",
      answer: "You can. We post real picks publicly. But you'll never see the 6-leggers, the analysis, or be part of the network. You're getting the appetizer, not the meal."
    },
    {
      question: "What if I share picks anyway?",
      answer: "The NDA is legally binding. More importantly, you'll be removed immediately and permanently. And the other 99 members will know why."
    },
    {
      question: "What if I don't make money?",
      answer: "Betting has variance. We're not guaranteeing you'll profit. We're giving you a 17% edge on 6-leg parlays when the industry hits 2-3%. What you do with that is on you."
    },
    {
      question: "Can I pay monthly?",
      answer: "No. Annual commitment only. This filters for serious people and keeps the community stable."
    },
    {
      question: "What payment do you accept?",
      answer: "Cryptocurrency only. No PayPal. No credit cards. No payment plans. If you're betting serious money on sports, you already know how to move crypto. If you don't, this probably isn't for you."
    },
    {
      question: "What's the refund policy?",
      answer: "There isn't one. You're a sports bettor. You understand risk. You could lose $10K on a single bet tonight and wake up tomorrow ready to go again. This is the same thing. You're betting $10K on a system that hits 17% on 6-leg parlays. Either you believe the numbers or you don't. We're not here to hold your hand or process refund requests. We're here to send picks to 100 serious bettors who don't need their money back because they're going to make it back and then some. If $10K feels like a risk you can't take, this isn't your room."
    },
    {
      question: "What happens after 100 members?",
      answer: "We close enrollment. Permanently. No waitlist. Check back if someone leaves."
    },
    {
      question: "Why is the delivery system 'not on clearnet'?",
      answer: "Books and others would prefer this didn't exist. We protect the infrastructure and the members."
    }
  ];

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="faq-section">
      <div className="container">
        <h2 className="section-title">Frequently Asked Questions</h2>
        <p className="section-subtitle">
          Common questions about the platform, pricing, and access.
        </p>

        <div className="faq-list">
          {faqs.map((faq, index) => (
            <div key={index} className={`faq-item ${openIndex === index ? 'open' : ''}`}>
              <button
                className="faq-question"
                onClick={() => toggleFAQ(index)}
              >
                <span>{faq.question}</span>
                <span className="faq-icon">{openIndex === index ? '−' : '+'}</span>
              </button>
              {openIndex === index && (
                <div className="faq-answer">
                  <p>{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FAQ;


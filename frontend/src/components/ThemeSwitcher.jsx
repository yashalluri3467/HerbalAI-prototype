import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useTheme } from '../ThemeContext';
import { Palette, Check, ChevronDown } from 'lucide-react';

const DROPDOWN_GAP = 8;
const VIEWPORT_PADDING = 12;
// Approximate height of each theme option row + container padding
const ESTIMATED_DROPDOWN_HEIGHT = 200;
const DROPDOWN_MIN_WIDTH = 220;

export default function ThemeSwitcher() {
  const { themeId, setThemeId, themes } = useTheme();
  const [open, setOpen] = useState(false);
  const btnRef = useRef(null);
  const dropdownRef = useRef(null);
  const [dropdownStyle, setDropdownStyle] = useState({});

  // Intelligently position the dropdown: flip up/down and clamp horizontally
  const updatePosition = useCallback(() => {
    if (!btnRef.current) return;

    const rect = btnRef.current.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    // Measure actual dropdown height if it's rendered, otherwise estimate
    const dropdownHeight = dropdownRef.current
      ? dropdownRef.current.offsetHeight
      : ESTIMATED_DROPDOWN_HEIGHT;
    const dropdownWidth = dropdownRef.current
      ? dropdownRef.current.offsetWidth
      : DROPDOWN_MIN_WIDTH;

    // Decide vertical placement: prefer below, flip to above if not enough space
    const spaceBelow = vh - rect.bottom - DROPDOWN_GAP;
    const spaceAbove = rect.top - DROPDOWN_GAP;
    const openBelow = spaceBelow >= dropdownHeight || spaceBelow >= spaceAbove;

    let top;
    if (openBelow) {
      top = rect.bottom + DROPDOWN_GAP;
      // Clamp so it doesn't go below viewport
      if (top + dropdownHeight > vh - VIEWPORT_PADDING) {
        top = vh - VIEWPORT_PADDING - dropdownHeight;
      }
    } else {
      top = rect.top - DROPDOWN_GAP - dropdownHeight;
      // Clamp so it doesn't go above viewport
      if (top < VIEWPORT_PADDING) {
        top = VIEWPORT_PADDING;
      }
    }

    // Horizontal: align right edge with button right edge, but clamp within viewport
    let left = rect.right - dropdownWidth;
    if (left < VIEWPORT_PADDING) {
      left = VIEWPORT_PADDING;
    }
    if (left + dropdownWidth > vw - VIEWPORT_PADDING) {
      left = vw - VIEWPORT_PADDING - dropdownWidth;
    }

    setDropdownStyle({
      position: 'fixed',
      top,
      left,
      zIndex: 99999,
      maxHeight: `${Math.max(vh - VIEWPORT_PADDING * 2 - DROPDOWN_GAP, 120)}px`,
      overflowY: 'auto',
    });
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (
        btnRef.current && !btnRef.current.contains(e.target) &&
        dropdownRef.current && !dropdownRef.current.contains(e.target)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Update position when opening and on scroll/resize
  useEffect(() => {
    if (open) {
      // Run twice: once immediately (estimated), once after render (measured)
      updatePosition();
      const raf = requestAnimationFrame(updatePosition);
      window.addEventListener('scroll', updatePosition, true);
      window.addEventListener('resize', updatePosition);
      return () => {
        cancelAnimationFrame(raf);
        window.removeEventListener('scroll', updatePosition, true);
        window.removeEventListener('resize', updatePosition);
      };
    }
  }, [open, updatePosition]);

  const currentTheme = themes.find((t) => t.id === themeId);

  return (
    <>
      <button
        ref={btnRef}
        className="theme-switcher-btn"
        onClick={() => setOpen(!open)}
        aria-label="Switch Interface Theme"
        title="Switch Interface Theme"
      >
        <Palette size={16} />
        <span className="theme-switcher-label">{currentTheme?.icon} {currentTheme?.label}</span>
        <ChevronDown size={14} className={`theme-chevron ${open ? 'open' : ''}`} />
      </button>

      {open && createPortal(
        <div
          ref={dropdownRef}
          className="theme-dropdown-portal"
          style={dropdownStyle}
        >
          {themes.map((t) => (
            <button
              key={t.id}
              className={`theme-option ${t.id === themeId ? 'active' : ''}`}
              onClick={() => {
                setThemeId(t.id);
                setOpen(false);
              }}
            >
              <span className="theme-option-icon">{t.icon}</span>
              <span className="theme-option-label">{t.label}</span>
              {t.id === themeId && <Check size={14} className="theme-check" />}
            </button>
          ))}
        </div>,
        document.body
      )}
    </>
  );
}

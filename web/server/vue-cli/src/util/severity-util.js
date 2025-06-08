const Severity = {
  CRITICAL: 1,
  HIGH: 2,
  MEDIUM: 3,
  LOW: 4,
  STYLE: 5,
  UNSPECIFIED: 6,

  toString(code) {
    switch (code) {
    case 1: return "critical";
    case 2: return "high";
    case 3: return "medium";
    case 4: return "low";
    case 5: return "style";
    case 6: return "unspecified";
    default: return "unknown";
    }
  }
};

export default Severity;

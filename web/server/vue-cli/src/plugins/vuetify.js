import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

const opts = {
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: { mdi },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: "#2280c3",
          secondary: "#2c87c7",
          accent: "#009688",
          error: "#f44336",
          warning: "#ff9800",
          info: "#3f51b5",
          success: "#4caf50",
          grey: "#9E9E9E"
        },
      },
    },
  },
};

const vuetify = createVuetify(opts);

export default vuetify;
// Tailwind settings for: about/index.html
// CDN build: https://cdn.tailwindcss.com?plugins=forms,container-queries
tailwind.config = {
      darkMode: 'class',
      theme: { extend: {
        colors: {
          'vibrant-iris':'#9580FF','primary':'#333e4d','slate-gray':'#4A5565','salmon-coral':'#FA8072',
          'tertiary':'#3d20a3','tertiary-container':'#553dba','surface':'#fcf8ff','surface-bright':'#fcf8ff',
          'surface-dim':'#dbd8e8','surface-variant':'#e3e0f1','surface-container':'#efecfc',
          'surface-container-low':'#f5f2ff','surface-container-high':'#e9e6f6',
          'surface-container-highest':'#e3e0f1','surface-container-lowest':'#ffffff',
          'soft-surface':'#F8FAFB','on-surface':'#1b1b26','on-surface-variant':'#44474c',
          'on-primary':'#ffffff','background':'#fcf8ff','on-background':'#1b1b26',
          'primary-fixed':'#d8e3f7','primary-fixed-dim':'#bcc7da','primary-container':'#4a5565',
          'on-primary-fixed':'#111c2a','on-primary-container':'#becadd','secondary':'#a23d34',
          'secondary-fixed':'#ffdad5','secondary-fixed-dim':'#ffb4aa','secondary-container':'#fc8274',
          'tertiary-fixed':'#e6deff','tertiary-fixed-dim':'#c9beff','on-tertiary':'#ffffff',
          'on-tertiary-container':'#ccc1ff','outline':'#75777c','outline-variant':'#c5c6cc',
          'deep-onyx':'#14141F','inverse-surface':'#302f3b','inverse-on-surface':'#f2efff',
        },
        borderRadius: { DEFAULT:'0.25rem', lg:'0.5rem', xl:'0.75rem', full:'9999px' },
        spacing: {
          xs:'0.5rem',sm:'1rem',md:'1.5rem',lg:'2rem',xl:'4rem',
          base:'10px',gutter:'20px','margin-desktop':'40px','margin-mobile':'16px',
        },
        fontFamily: {
          'display-lg':['Inter','sans-serif'],'headline-lg':['Inter','sans-serif'],
          'headline-md':['Inter','sans-serif'],'body-lg':['Inter','sans-serif'],
          'body-md':['Inter','sans-serif'],'label-md':['Plus Jakarta Sans','sans-serif'],
        },
        fontSize: {
          'display-lg':['48px',{lineHeight:'56px',letterSpacing:'-0.02em',fontWeight:'700'}],
          'headline-lg':['32px',{lineHeight:'40px',letterSpacing:'-0.01em',fontWeight:'600'}],
          'headline-md':['20px',{lineHeight:'28px',fontWeight:'600'}],
          'body-lg':['16px',{lineHeight:'24px',fontWeight:'400'}],
          'body-md':['14px',{lineHeight:'20px',fontWeight:'400'}],
          'label-md':['12px',{lineHeight:'16px',letterSpacing:'0.05em',fontWeight:'600'}],
        },
      }},
    }

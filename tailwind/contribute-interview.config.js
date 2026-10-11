// Tailwind settings for: contribute/interview/index.html
// CDN build: https://cdn.tailwindcss.com
tailwind.config = {
      darkMode: 'class',
      corePlugins: { preflight: true },
      theme: { extend: {
        colors: {
          'vibrant-iris':'#9580FF','iris-deep':'#6c5ce7','primary':'#333e4d','slate-gray':'#4A5565',
          'tertiary':'#3d20a3','surface':'#fcf8ff','surface-container':'#efecfc','surface-container-low':'#f5f2ff',
          'surface-container-lowest':'#ffffff','on-surface':'#1b1b26','on-background':'#1b1b26','tertiary-fixed':'#e6deff',
        },
        spacing: { xs:'0.5rem',sm:'1rem',md:'1.5rem',lg:'2rem',xl:'4rem',base:'10px','margin-desktop':'40px','margin-mobile':'16px' },
        fontFamily: { 'body-md':['Inter','sans-serif'],'label-md':['Plus Jakarta Sans','sans-serif'],'headline-md':['Inter','sans-serif'],'headline-lg':['Inter','sans-serif'] },
        fontSize: {
          'headline-lg':['32px',{lineHeight:'40px',letterSpacing:'-0.01em',fontWeight:'600'}],
          'headline-md':['20px',{lineHeight:'28px',fontWeight:'600'}],
          'body-lg':['16px',{lineHeight:'24px',fontWeight:'400'}],
          'body-md':['14px',{lineHeight:'20px',fontWeight:'400'}],
          'label-md':['12px',{lineHeight:'16px',letterSpacing:'0.05em',fontWeight:'600'}],
        },
      }},
    }

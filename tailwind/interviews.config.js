// Tailwind settings for: interviews/*
// CDN build: https://cdn.tailwindcss.com?plugins=forms,container-queries
tailwind.config = {
      darkMode:'class',
      theme:{extend:{
        colors:{
          'vibrant-iris':'#9580FF','primary':'#333e4d','slate-gray':'#4A5565',
          'tertiary':'#3d20a3','tertiary-container':'#553dba','surface':'#fcf8ff',
          'surface-container':'#efecfc','surface-container-low':'#f5f2ff',
          'surface-container-high':'#e9e6f6','surface-container-highest':'#e3e0f1',
          'surface-container-lowest':'#ffffff','soft-surface':'#F8FAFB',
          'on-surface':'#1b1b26','on-surface-variant':'#44474c','background':'#fcf8ff',
          'on-background':'#1b1b26','primary-fixed':'#d8e3f7','secondary':'#a23d34',
          'secondary-fixed-dim':'#ffb4aa','tertiary-fixed':'#e6deff',
          'tertiary-fixed-dim':'#c9beff','outline':'#75777c','outline-variant':'#c5c6cc',
        },
        borderRadius:{DEFAULT:'0.25rem',lg:'0.5rem',xl:'0.75rem',full:'9999px'},
        spacing:{xs:'0.5rem',sm:'1rem',md:'1.5rem',lg:'2rem',xl:'4rem',base:'10px',gutter:'20px','margin-desktop':'40px','margin-mobile':'16px'},
        fontFamily:{
          'display-lg':['Inter'],'headline-lg':['Inter'],'headline-md':['Inter'],
          'body-lg':['Inter'],'body-md':['Inter'],'label-md':['Plus Jakarta Sans'],
        },
        fontSize:{
          'display-lg':['48px',{lineHeight:'56px',letterSpacing:'-0.02em',fontWeight:'700'}],
          'headline-lg':['32px',{lineHeight:'40px',letterSpacing:'-0.01em',fontWeight:'600'}],
          'headline-md':['20px',{lineHeight:'28px',fontWeight:'600'}],
          'body-lg':['16px',{lineHeight:'24px',fontWeight:'400'}],
          'body-md':['14px',{lineHeight:'20px',fontWeight:'400'}],
          'label-md':['12px',{lineHeight:'16px',letterSpacing:'0.05em',fontWeight:'600'}],
        },
      }},
    }

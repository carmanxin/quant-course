(() => {
  const details = document.querySelectorAll('details.scb-out');
  return Array.from(details).map(d => {
    const parent = d.parentElement;
    const attrs = {};
    for (const a of parent.attributes) attrs[a.name] = a.value.slice(0, 60);
    return {
      parentClass: parent.className,
      parentAttrs: attrs,
      open: d.open,
      defaultOpen: d.hasAttribute('open'),
    };
  });
})()

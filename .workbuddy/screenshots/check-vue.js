(() => {
  const root = document.querySelectorAll('.scb');
  const results = [];
  for (const el of root) {
    const inst = el.__vueParentComponent;
    results.push({
      hasInst: !!inst,
      outputB64Prop: inst && inst.props ? inst.props.outputB64 : 'no-props',
      props: inst && inst.props ? Object.keys(inst.props) : [],
      fetchedOutput: inst && inst.setupState ? inst.setupState.fetchedOutput : 'no-setup',
      output: inst && inst.setupState ? inst.setupState.output : 'no-setup',
    });
  }
  return JSON.stringify(results, null, 2);
})()

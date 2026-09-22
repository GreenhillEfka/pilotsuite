/* Draft decisions are local until an explicit save. No HA actuation. */
class SelectionDraft {
  constructor(inventory) {
    this.inventory = inventory;
    this.original = new Map([...inventory.items, ...inventory.missing].map(item => [item.entity_id, item.decision]));
    this.decisions = new Map(this.original);
  }
  set(id, decision) {
    if (!this.original.has(id) || !['relevant', 'ignored', 'unreviewed'].includes(decision)) throw new Error('Ungültige Auswahl');
    this.decisions.set(id, decision);
  }
  get changes() {
    return Object.fromEntries([...this.decisions].filter(([id, value]) => this.original.get(id) !== value));
  }
  get dirty() { return Object.keys(this.changes).length > 0; }
  recommend() {
    for (const item of this.inventory.items) {
      if (item.recommended && this.decisions.get(item.entity_id) === 'unreviewed') this.set(item.entity_id, 'relevant');
    }
  }
}
if (typeof module !== 'undefined') module.exports = { SelectionDraft };

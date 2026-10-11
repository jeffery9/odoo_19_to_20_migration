/** @odoo-module **/
export class Legacy extends Component {
    async loadData() {
        return this._rpc({model: 'demo.legacy', method: 'search_read'});
    }
}

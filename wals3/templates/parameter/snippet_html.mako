<%inherit file="../snippet.mako"/>
<%namespace name="util" file="../util.mako"/>

<% total = 0 %>
<table class="table table-hover table-condensed domain" style="width: auto;">
    <thead>
        <tr>
            <th colspan="3"><a class="button btn" href="${request.resource_url(ctx)}">Go to map</a></th>
        </tr>
        <tr>
            <th>&nbsp;</th><th>Value</th><th>Representation</th>
        </tr>
    </thead>
    <tbody>
        % for de in ctx.domain:
        <tr>
            <% total += len(de.values) %>
            <td>${h.map_marker_img(request, de)}</td>
            <td>${de.description or de.name}</td>
            <td class="right">${len(de.values)}</td>
        </tr>
        % endfor
        <tr>
            <td colspan="2" class="right"><b>Total:</b></td>
            <td class="right">${total}</td>
        </tr>
    </tbody>
</table>

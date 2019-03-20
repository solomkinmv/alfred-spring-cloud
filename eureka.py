# encoding: utf-8

from workflow import Workflow, ICON_WEB, ICON_WARNING, web
import argparse

log = None


def get_apps(eureka_url):
    url = eureka_url + '/eureka/apps'
    params = dict(Accept='application/json')
    r = web.get(url, headers=params)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON
    result = r.json()
    apps = result['applications']['application']

    log_apps('Fetched apps: %s', apps)
    return apps


def log_apps(message, apps):
    log.debug(message, map(lambda app: app['name'], apps))


def search_key_for_post(app):
    """Generate a string search key for a app"""
    elements = [app['name']]
    # todo: add status
    return u' '.join(elements)


def main(wf):
    log.debug('Started')

    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional (nargs='?') --setkey argument and save its
    # value to 'eureka_url' (dest). This will be called from a separate "Run Script"
    # action with the eureka_url key
    parser.add_argument('--seturl', dest='eureka_url', nargs='?', default=None)
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # Save the provided eureka url
    ####################################################################

    # decide what to do based on arguments
    if args.eureka_url:  # Script was passed an eureka_url
        # save the key
        wf.settings['eureka_url'] = args.eureka_url
        return 0  # 0 means script exited cleanly

    ####################################################################
    # Check that we have an eureka_url key saved
    ####################################################################

    eureka_url = wf.settings.get('eureka_url', None)
    if not eureka_url:  # eureka_url key has not yet been set
        wf.add_item('No Eureka url key set.',  # todo: rename
                    'Please use eurekaseturl to set your Eureka url key.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    ####################################################################
    # View/filter Eureka apps
    ####################################################################

    query = args.query

    # retrieve apps
    def wrapper():
        """`cached_data` can only take a bare callable (no args),
        so we need to wrap callables needing arguments in a function
        that needs none.
        """
        return get_apps(eureka_url)

    apps = wf.cached_data('apps', wrapper, max_age=10)

    # If script was passed a query, use it to filter apps
    if query:
        log_apps('Before filter: %s', apps)
        apps = wf.filter(query, apps, key=search_key_for_post)
        log_apps('After filter: %s', apps)

    if not apps:  # we have no data to show, so show a warning and stop
        wf.add_item('No apps found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for app in apps:
        instance = app['instance'][0]
        wf.add_item(title=app['name'],
                    subtitle=instance['hostName'],
                    arg=instance['statusPageUrl'],
                    valid=True,
                    icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    wf.run(main)
    # sys.exit(wf.run(main))
